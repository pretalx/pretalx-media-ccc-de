from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from pretalx.common.mixins.views import PermissionRequired
from pretalx.submission.models import Submission, SubmissionStates

from .forms import MediaCCCDeSettingsForm, MediaCCCDeUrlForm
from .recording import MediaCCCDe


class MediaCCCDeSettings(PermissionRequired, FormView):
    form_class = MediaCCCDeSettingsForm
    permission_required = 'orga.change_settings'
    template_name = 'pretalx_media_ccc_de/settings.html'

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', 'save')
        if action == 'regenerate':
            messages.success(
                request, _('Looking for new talks – this may take a while.')
            )
            MediaCCCDe(request.event).fill_recording_urls()

        elif action.startswith('url'):
            code = action.lstrip('url_')
            try:
                submission = request.event.submissions.get(code=code)
            except Submission.DoesNotExist:
                messages.error(_('Could not find this talk.'))
                return super().post(request, *args, **kwargs)

            form = MediaCCCDeUrlForm(request.POST, submission=submission)
            if not form.is_valid():
                messages.error(form.errors)
            else:
                request.event.settings.set(
                    f'media_ccc_de_url_{submission.code}',
                    form.cleaned_data['media_ccc_de_url'],
                )
                messages.success(_('The URL for this talk was overridden.'))

        return super().post(request, *args, **kwargs)

    def get_object(self):
        return self.request.event

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {'obj': self.request.event, 'attribute_name': 'settings', **kwargs}

    def get_context_data(self):
        kwargs = super().get_context_data()
        kwargs['url_forms'] = [
            MediaCCCDeUrlForm(submission=submission)
            for submission in self.request.event.talks
        ]
        return kwargs
