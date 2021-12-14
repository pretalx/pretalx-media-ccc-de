import json
from contextlib import suppress

import requests
from django_scopes import scope, scopes_disabled
from pretalx.celery_app import app
from pretalx.event.models import Event
from pretalx.submission.models import Submission


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
        apply_api_response(event=event, response=structure)


def apply_api_response(event, response):
    for talk in response.get("events", []):
        if talk.get("frontend_link"):
            submission = None
            link = talk.get("link")
            if link:
                with suppress(Submission.DoesNotExist):
                    submission = Submission.objects.get(
                        event=event,
                        code__iexact=talk["link"]
                        .rstrip("/")
                        .rsplit("/", maxsplit=1)[-1],
                    )
            if not submission:
                with suppress(Submission.DoesNotExist):
                    submission = Submission.objects.get(
                        event=event, pk__iexact=talk["slug"].split("-")[1]
                    )
                with suppress(Submission.DoesNotExist):
                    submission = Submission.objects.get(
                        event=event, code__iexact=talk["slug"].split("-")[1]
                    )
            if submission:
                key = f"media_ccc_de_url_{submission.code}"
                if not event.settings.get(key):
                    event.settings.set(key, talk["frontend_link"])
