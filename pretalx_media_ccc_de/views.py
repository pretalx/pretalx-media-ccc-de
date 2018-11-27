from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from pretalx.common.mixins.views import PermissionRequired

from .forms import MediaCCCDeSettingsForm
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
        if request.POST.get('action', 'save') == 'regenerate':
            messages.success(request, _('Looking for new talks – this may take a while.'))
            MediaCCCDe(request.event).fill_recording_urls()
            
        return super().post(request, *args, **kwargs)

    def get_object(self):
        return self.request.event

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {
            'obj': self.request.event,
            'attribute_name': 'settings',
            **kwargs
        }
