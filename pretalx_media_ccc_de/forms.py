from django import forms
from django.utils.translation import ugettext_lazy as _
from hierarkey.forms import HierarkeyForm


class MediaCCCDeSettingsForm(HierarkeyForm):

    media_ccc_de_id = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        event = kwargs.get('obj')
        url = 'https://media.ccc.de/public/conferences/{slug}'.format(slug=event.settings.media_ccc_de_id or event.slug)
        self.fields['media_ccc_de_id'].help_text = _('The slug or ID used for your event in the media.ccc.de API – for example your event slug. Your event\'s data has to be available at <a href="{url}">{url}</a>').format(url=url)
        if not event.settings.media_ccc_de_id:
            self.fields['media_ccc_de_id'].default = event.slug
