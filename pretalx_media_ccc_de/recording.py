from pretalx.agenda.recording import BaseRecordingProvider
from pretalx.submission.models import Submission


class MediaCCCDe(BaseRecordingProvider):
    def fill_recording_urls(self):
        if not self.event.settings.media_ccc_de_id:
            return None

        response = requests.get(
            f'https://media.ccc.de/public/conferences/{self.event.settings.media_ccc_de_id}'
        )
        if not response.status_code == 200:
            return None

        structure = json.loads(response.content.decode())
        for event in structure.get('events', []):
            if event.get('frontend_link'):
                with suppress(Submission.DoesNotExist):
                    talk = Submission.objects.get(
                        event=self.event, pk=event['slug'].split('-')[1]
                    )
                    self.event.settings.set(
                        f'media_ccc_de_url_{talk.slug}', event['frontend_link']
                    )

    def get_recording(self, submission):
        if not self.event.settings.media_ccc_de_id:
            return None
        path = self.event.settings.get(f'media_ccc_de_url_{submission.slug}')
        if not path:
            self.fill_recording_urls()
            path = self.event.settings.get(f'media_ccc_de_url_{submission.slug}')
        if not path:
            return None
        iframe = f'<div class="embed-responsive embed-responsive-16by9"><iframe src="{path}/oembed" frameborder="0" allowfullscreen></iframe></div>'
        csp_header = 'https://media.ccc.de'
        return {'iframe': iframe, 'csp_header': csp_header}
