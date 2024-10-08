from pretalx.agenda.recording import BaseRecordingProvider

from .tasks import task_refresh_recording_urls


class MediaCCCDe(BaseRecordingProvider):
    def fill_recording_urls(self):
        task_refresh_recording_urls.apply_async(
            kwargs={"event_slug": self.event.slug}, ignore_result=True
        )

    def get_recording(self, submission):
        data = getattr(submission, "media_ccc_de_link", None)
        if data:
            return {
                "iframe": data.iframe,
                "csp_header": "https://media.ccc.de",
            }
