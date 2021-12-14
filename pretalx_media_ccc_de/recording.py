from pretalx.agenda.recording import BaseRecordingProvider

from .tasks import task_refresh_recording_urls


class MediaCCCDe(BaseRecordingProvider):
    def fill_recording_urls(self):
        task_refresh_recording_urls.apply_async(kwargs={"event_slug": self.event.slug})

    def get_recording(self, submission):
        path = self.event.settings.get(f"media_ccc_de_url_{submission.code}")
        if not path:
            return None
        iframe = f'<div class="embed-responsive embed-responsive-16by9"><iframe src="{path}/oembed" frameborder="0" allowfullscreen></iframe></div>'
        csp_header = "https://media.ccc.de"
        return {"iframe": iframe, "csp_header": csp_header}
