from django.conf.urls import include, url
from pretalx.event.models.event import SLUG_CHARS

from .views import MediaCCCDeSettings

urlpatterns = [
    url(fr'^orga/event/(?P<event>[{SLUG_CHARS}]+)/settings/p/media.ccc.de/$', MediaCCCDeSettings.as_view(), name='settings')
]
