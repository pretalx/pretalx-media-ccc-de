from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class PluginApp(AppConfig):
    name = "pretalx_media_ccc_de"
    verbose_name = "media.ccc.de recordings"

    class PretalxPluginMeta:
        name = gettext_lazy("media.ccc.de recordings")
        author = "Tobias Kunze"
        description = gettext_lazy(
            "Pull recordings from media.ccc.de and embed them in talk pages"
        )
        visible = True
        version = "1.1.0"

    def ready(self):
        from . import signals  # NOQA
        from . import tasks  # NOQA
