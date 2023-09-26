import json
from contextlib import suppress

import requests
from django_scopes import scope, scopes_disabled
from pretalx.celery_app import app
from pretalx.event.models import Event
from pretalx.submission.models import Submission

from .models import MediaCccDeLink


@app.task()
def task_refresh_recording_urls(event_slug):
    try:
        with scopes_disabled():
            event = Event.objects.get(slug__iexact=event_slug)
    except Event.DoesNotExist:
        return

    with scope(event=event):
        if not event.settings.media_ccc_de_id:
            event.settings.media_ccc_de_id = event.slug

        response = requests.get(
            f"https://media.ccc.de/public/conferences/{event.settings.media_ccc_de_id}"
        )
        if not response.status_code == 200:
            return None

        structure = json.loads(response.content.decode())

        for api_data in structure.get("events", []):
            if not api_data.get("frontend_link"):
                continue

            submission = find_submission(event, api_data)
            if submission:
                MediaCccDeLink.objects.update_or_create(
                    submission=submission,
                    defaults={
                        "url": api_data["frontend_link"],
                        "release_date": api_data["release_date"],
                        "duration_seconds": api_data["duration"],
                        "thumbnail_url": api_data["poster_url"],
                    },
                )


def find_submission(event, api_data):
    link = api_data.get("link")
    if link:
        with suppress(Submission.DoesNotExist):
            return Submission.objects.get(
                event=event,
                code__iexact=link.rstrip("/").rsplit("/", maxsplit=1)[-1],
            )
    with suppress(Submission.DoesNotExist):
        return Submission.objects.get(
            event=event, pk__iexact=api_data["slug"].split("-")[1]
        )
    with suppress(Submission.DoesNotExist):
        return Submission.objects.get(
            event=event, code__iexact=api_data["slug"].split("-")[1]
        )
