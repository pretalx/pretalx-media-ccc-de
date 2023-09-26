from django import forms
from django.utils.translation import gettext_lazy as _
from hierarkey.forms import HierarkeyForm

from .models import MediaCccDeLink


class MediaCCCDeSettingsForm(HierarkeyForm):
    media_ccc_de_id = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        event = kwargs.get("obj")
        url = "https://media.ccc.de/public/conferences/{slug}".format(
            slug=event.settings.media_ccc_de_id or event.slug
        )
        self.fields["media_ccc_de_id"].help_text = _(
            'The slug or ID used for your event in the media.ccc.de API – defaults to your event slug. Your event\'s data has to be available at <a href="{url}">{url}</a>'
        ).format(url=url)
        if not event.settings.media_ccc_de_id:
            self.fields["media_ccc_de_id"].initial = event.slug


class MediaCCCDeUrlForm(forms.Form):
    def __init__(self, *args, event=None, **kwargs):
        if not event or not event.current_schedule:
            return super().__init__(*args, **kwargs)
        self.event = event
        super().__init__(*args, **kwargs)

        self.talks = (
            event.current_schedule.talks.all()
            .filter(is_visible=True, submission__isnull=False)
            .order_by("start")
        )
        video_data = {
            v.submission.code: v.url
            for v in MediaCccDeLink.objects.filter(submission__event=event)
        }
        s = _("Go to video.")
        p = _("Go to talk page.")
        for talk in self.talks:
            link = video_data.get(talk.submission.code)
            help_text = f'<a href="{talk.submission.urls.public.full()}">{p}</a>'
            if link:
                help_text += f' | <a href="{link}">{s}</a>'
            self.fields[f"video_id_{talk.submission.code}"] = forms.URLField(
                required=False,
                label=talk.submission.title,
                widget=forms.URLInput(attrs={"placeholder": ""}),
                initial=link,
                help_text=help_text,
            )

    def save(self):
        for talk in self.talks:
            url = self.cleaned_data.get(f"video_id_{talk.submission.code}")
            if url:
                MediaCccDeLink.objects.update_or_create(
                    submission=talk.submission, defaults={"url": url}
                )
            else:
                MediaCccDeLink.objects.filter(submission=talk.submission).delete()
