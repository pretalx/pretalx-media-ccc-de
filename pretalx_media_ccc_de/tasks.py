import json
from contextlib import suppress
from functools import cached_property

import requests
from django_scopes import scope, scopes_disabled

from pretalx.celery_app import app
from pretalx.event.models import Event
from pretalx.submission.models import Submission

from .models import MediaCccDeLink


@app.task(name="pretalx_media_ccc_de.refresh_recording_urls")
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
        if response.status_code != 200:
            return None

        structure = json.loads(response.text)
        submission_finder = SubmissionFinder(event)

        for api_data in structure.get("events", []):
            if not api_data.get("frontend_link"):
                continue

            submission = submission_finder.find(api_data)
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


class SubmissionFinder:
    def __init__(self, event):
        self.event = event

    def find(self, api_data):
        if (guid := api_data.get("guid")) and guid in self.submissions_by_uuid:
            return self.submissions_by_uuid[guid]

        if link := api_data.get("link"):
            with suppress(Submission.DoesNotExist):
                return Submission.objects.get(
                    event=self.event,
                    code__iexact=link.rstrip("/").rsplit("/", maxsplit=1)[-1],
                )
        with suppress(Submission.DoesNotExist):
            return Submission.objects.get(
                event=self.event, pk__iexact=api_data["slug"].split("-")[1]
            )
        with suppress(Submission.DoesNotExist):
            return Submission.objects.get(
                event=self.event, code__iexact=api_data["slug"].split("-")[1]
            )

    @cached_property
    def submissions_by_uuid(self):
        # UUIDs are a property of Slots, but are (currently) only generated from information about the
        # respective Submission (and pretalx instance)
        slots = self.event.current_schedule.scheduled_talks
        return {str(slot.uuid): slot.submission for slot in slots}
