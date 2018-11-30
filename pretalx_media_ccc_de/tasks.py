import json
from contextlib import suppress

import requests
from pretalx.celery_app import app
from pretalx.event.models import Event
from pretalx.submission.models import Submission


@app.task()
def task_refresh_recording_urls(event_slug):
    try:
        event = Event.objects.get(slug=event_slug)
    except Event.DoesNotExist:
        return

    if not event.settings.media_ccc_de_id:
        event.settings.media_ccc_de_id = event.slug

    response = requests.get(
        f'https://media.ccc.de/public/conferences/{event.settings.media_ccc_de_id}'
    )
    if not response.status_code == 200:
        return None

    structure = json.loads(response.content.decode())
    for talk in structure.get('events', []):
        if talk.get('frontend_link'):
            with suppress(Submission.DoesNotExist):
                submission = Submission.objects.get(
                    event=event, pk=talk['slug'].split('-')[1]
                )
                key = f'media_ccc_de_url_{submission.code}'
                if not event.settings.get(key):
                    event.settings.set(
                        key, talk['frontend_link']
                    )
