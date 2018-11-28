from datetime import timedelta

from django.dispatch import receiver
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from pretalx.agenda.signals import register_recording_provider
from pretalx.common.signals import periodic_task
from pretalx.event.models import Event
from pretalx.orga.signals import nav_event_settings

from .recording import MediaCCCDe


@receiver(register_recording_provider)
def media_ccc_de_provider(sender, **kwargs):
    return MediaCCCDe(sender)


@receiver(periodic_task)
def gather_media_ccc_de_urls(sender, request, **kwargs):
    active_events = Event.objects.filter(plugins__icontains='media_ccc_de')
    for event in active_events:
        if not 'media_ccc_de' in event.get_plugins() or now().date() < event.date_from:
            continue
        last_check = event.settings.media_ccc_de_check
        event_active = (now().date() - event.date_to) <= timedelta(days=7)
        if not last_check or (now() - last_check > timedelta(hours=1) and event_active):
            MediaCCCDe(event).fill_recording_urls()


@receiver(nav_event_settings)
def media_ccc_de_settings(sender, request, **kwargs):
    if not request.user.has_perm('orga.change_settings', request.event):
        return []
    return [{
        'label': 'media.ccc.de',
        'url': reverse('plugins:pretalx_media_ccc_de:settings', kwargs={'event': request.event.slug}),
        'active': request.resolver_match.url_name == 'plugins:pretalx_media_ccc_de:settings'
    }]
