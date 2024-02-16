from django.urls import re_path
from pretalx.event.models.event import SLUG_REGEX

from .views import MediaCCCDeSettings

urlpatterns = [
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/settings/p/media.ccc.de/$",
        MediaCCCDeSettings.as_view(),
        name="settings",
    )
]
