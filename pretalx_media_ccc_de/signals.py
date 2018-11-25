from django.dispatch import receiver
from pretalx.agenda.signals import register_recording_provider

from .recording import MediaCCCDe


@receiver(register_recording_provider)
def media_ccc_de_provider(sender, request):
    return MediaCCCDe(request)
