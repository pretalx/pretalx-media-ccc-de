from datetime import timedelta

from django.dispatch import receiver
from django.utils.timezone import now
from pretalx.agenda.signals import register_recording_provider
from pretalx.common.signals import periodic_task
from pretalx.event.models import Event

from .recording import MediaCCCDe


@receiver(register_recording_provider)
def media_ccc_de_provider(sender, request):
    return MediaCCCDe(request)


@receiver(periodic_task)
def gather_media_ccc_de_urls(sender, request):
    active_events = Event.objects.filter(plugins__icontains='media_ccc_de')
    for event in active_events:
        if not 'media_ccc_de' in event.get_plugins():
            continue
        last_check = event.settings.media_ccc_de_check
        event_active = (now().date() - event.date_from) <= timedelta(days=7)
        if not last_check or (now() - last_check > timedelta(hours=1) and event_active):
            MediaCCCDe(event).fill_recording_urls()
