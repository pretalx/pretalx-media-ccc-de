import json
from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse
from django_scopes import scope, scopes_disabled

from pretalx_media_ccc_de.models import MediaCccDeLink
from pretalx_media_ccc_de.recording import MediaCCCDe
from pretalx_media_ccc_de.signals import media_ccc_de_provider
from pretalx_media_ccc_de.tasks import SubmissionFinder, task_refresh_recording_urls

SETTINGS_URL_NAME = "plugins:pretalx_media_ccc_de:settings"


@pytest.mark.django_db
def test_orga_can_access_settings(orga_client, event):
    response = orga_client.get(
        reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug}),
        follow=True,
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_reviewer_cannot_access_settings(review_client, event):
    response = review_client.get(
        reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug}),
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_orga_can_save_settings(orga_client, event):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.post(
        url,
        {"media_ccc_de_id": "my-conference", "action": "save"},
        follow=True,
    )
    assert response.status_code == 200
    event.settings.flush()
    assert event.settings.media_ccc_de_id == "my-conference"


@pytest.mark.django_db
@patch("pretalx_media_ccc_de.recording.task_refresh_recording_urls")
def test_orga_can_regenerate(mock_task, orga_client, event):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.post(
        url,
        {"media_ccc_de_id": event.slug, "action": "regenerate"},
        follow=True,
    )
    assert response.status_code == 200
    mock_task.apply_async.assert_called_once()


@pytest.mark.django_db
def test_orga_can_save_urls(orga_client, event, schedule_with_talk, submission):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.post(
        url,
        {
            "action": "urls",
            f"video_id_{submission.code}": "https://media.ccc.de/v/test-talk",
        },
        follow=True,
    )
    assert response.status_code == 200
    with scopes_disabled():
        assert MediaCccDeLink.objects.filter(submission=submission).exists()
        assert (
            MediaCccDeLink.objects.get(submission=submission).url
            == "https://media.ccc.de/v/test-talk"
        )


@pytest.mark.django_db
def test_orga_can_clear_url(orga_client, event, schedule_with_talk, submission):
    with scopes_disabled():
        MediaCccDeLink.objects.create(
            submission=submission, url="https://media.ccc.de/v/old"
        )
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.post(
        url,
        {"action": "urls", f"video_id_{submission.code}": ""},
        follow=True,
    )
    assert response.status_code == 200
    with scopes_disabled():
        assert not MediaCccDeLink.objects.filter(submission=submission).exists()


@pytest.mark.django_db
def test_settings_page_shows_url_form_with_schedule(
    orga_client, event, schedule_with_talk
):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.get(url)
    assert response.status_code == 200
    assert "url_form" in response.context


@pytest.mark.django_db
def test_settings_page_no_url_form_without_schedule(orga_client, event):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.get(url)
    assert response.status_code == 200
    assert "url_form" not in response.context or response.context["url_form"] is None


@pytest.mark.django_db
def test_media_ccc_de_link_iframe(submission):
    with scopes_disabled():
        link = MediaCccDeLink.objects.create(
            submission=submission, url="https://media.ccc.de/v/test-talk"
        )
    assert "iframe" in link.iframe
    assert "https://media.ccc.de/v/test-talk/oembed" in link.iframe


@pytest.mark.django_db
def test_media_ccc_de_link_serialize(submission):
    with scopes_disabled():
        link = MediaCccDeLink.objects.create(
            submission=submission,
            url="https://media.ccc.de/v/test-talk",
            duration_seconds=1800,
        )
    data = link.serialize()
    assert data["submission"] == submission.code
    assert data["url"] == "https://media.ccc.de/v/test-talk"
    assert data["duration_seconds"] == 1800
    assert data["release_date"] is None


@pytest.mark.django_db
def test_recording_provider_get_recording_with_link(event, submission):
    with scopes_disabled():
        MediaCccDeLink.objects.create(
            submission=submission, url="https://media.ccc.de/v/test-talk"
        )
        submission = (
            type(submission)
            .objects.select_related("media_ccc_de_link")
            .get(pk=submission.pk)
        )
    provider = MediaCCCDe(event)
    result = provider.get_recording(submission)
    assert result is not None
    assert "iframe" in result
    assert result["csp_header"] == "https://media.ccc.de"


@pytest.mark.django_db
def test_recording_provider_get_recording_without_link(event, submission):
    provider = MediaCCCDe(event)
    result = provider.get_recording(submission)
    assert result is None


@pytest.mark.django_db
@patch("pretalx_media_ccc_de.tasks.requests.get")
def test_task_refresh_creates_links(mock_get, event, submission, schedule_with_talk):
    event.settings.media_ccc_de_id = "testconf"
    with scopes_disabled():
        slot = schedule_with_talk.talks.first()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = json.dumps(
        {
            "events": [
                {
                    "guid": str(slot.uuid),
                    "frontend_link": "https://media.ccc.de/v/test-talk",
                    "release_date": "2024-01-01T00:00:00Z",
                    "duration": 1800,
                    "poster_url": "https://media.ccc.de/thumb.jpg",
                    "slug": "test-123",
                }
            ]
        }
    )
    mock_get.return_value = mock_response
    task_refresh_recording_urls(event.slug)
    with scopes_disabled():
        assert MediaCccDeLink.objects.filter(submission=submission).exists()
        link = MediaCccDeLink.objects.get(submission=submission)
        assert link.url == "https://media.ccc.de/v/test-talk"
        assert link.duration_seconds == 1800


@pytest.mark.django_db
@patch("pretalx_media_ccc_de.tasks.requests.get")
def test_task_refresh_handles_missing_event(mock_get):
    task_refresh_recording_urls("nonexistent-event")
    mock_get.assert_not_called()


@pytest.mark.django_db
@patch("pretalx_media_ccc_de.tasks.requests.get")
def test_task_refresh_handles_api_error(mock_get, event):
    event.settings.media_ccc_de_id = "testconf"
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    result = task_refresh_recording_urls(event.slug)
    assert result is None


@pytest.mark.django_db
def test_submission_finder_by_link(event, submission, schedule_with_talk):
    with scope(event=event):
        finder = SubmissionFinder(event)
        api_data = {
            "link": f"https://example.com/talk/{submission.code}",
            "slug": "irrelevant-123",
        }
        result = finder.find(api_data)
    assert result == submission


@pytest.mark.django_db
def test_submission_finder_by_code_in_slug(event, submission, schedule_with_talk):
    with scope(event=event):
        finder = SubmissionFinder(event)
        api_data = {"slug": f"talk-{submission.code}", "link": ""}
        result = finder.find(api_data)
    assert result == submission


@pytest.mark.django_db
def test_submission_finder_no_match(event, submission, schedule_with_talk):
    with scope(event=event):
        finder = SubmissionFinder(event)
        api_data = {"slug": "talk-ZZZZZ", "link": ""}
        result = finder.find(api_data)
    assert result is None


@pytest.mark.django_db
def test_recording_provider_signal(event):
    result = media_ccc_de_provider(event)
    assert isinstance(result, MediaCCCDe)


@pytest.mark.django_db
@patch("pretalx_media_ccc_de.tasks.requests.get")
def test_task_refresh_sets_default_id(mock_get, event):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = json.dumps({"events": []})
    mock_get.return_value = mock_response
    task_refresh_recording_urls(event.slug)
    event.settings.flush()
    assert event.settings.media_ccc_de_id == event.slug


@pytest.mark.django_db
@patch("pretalx_media_ccc_de.tasks.requests.get")
def test_task_refresh_skips_events_without_frontend_link(
    mock_get, event, submission, schedule_with_talk
):
    event.settings.media_ccc_de_id = "testconf"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = json.dumps({"events": [{"guid": "abc", "slug": "test-123"}]})
    mock_get.return_value = mock_response
    task_refresh_recording_urls(event.slug)
    with scopes_disabled():
        assert not MediaCccDeLink.objects.filter(submission=submission).exists()
