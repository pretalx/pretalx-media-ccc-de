import datetime as dt

from django.dispatch import receiver
from django.urls import reverse
from django.utils.timezone import now
from django_scopes import scope, scopes_disabled

from pretalx.agenda.signals import register_recording_provider
from pretalx.common.signals import minimum_interval, periodic_task
from pretalx.event.models import Event
from pretalx.orga.signals import nav_event_settings

from .recording import MediaCCCDe


@receiver(register_recording_provider)
def media_ccc_de_provider(sender, **kwargs):
    return MediaCCCDe(sender)


@receiver(periodic_task)
@minimum_interval(minutes_after_success=60)
def gather_media_ccc_de_urls(sender, **kwargs):
    with scopes_disabled():
        active_events = Event.objects.filter(plugins__icontains="media_ccc_de")
    for event in active_events:
        with scope(event=event):
            if "pretalx_media_ccc_de" not in event.plugin_list:
                continue
            if now().date() < event.date_from:
                continue
            if now().date() - event.date_to > dt.timedelta(days=7):
                continue
            MediaCCCDe(event).fill_recording_urls()


@receiver(nav_event_settings)
def media_ccc_de_settings(sender, request, **kwargs):
    if not request.user.has_perm("event.update_event", request.event):
        return []
    return [
        {
            "label": "media.ccc.de",
            "url": reverse(
                "plugins:pretalx_media_ccc_de:settings",
                kwargs={"event": request.event.slug},
            ),
            "active": request.resolver_match.url_name
            == "plugins:pretalx_media_ccc_de:settings",
        }
    ]
