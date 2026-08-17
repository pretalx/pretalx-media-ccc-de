from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from pretalx.common.ui import Button
from pretalx.common.views.mixins import PermissionRequired

from .forms import MediaCCCDeSettingsForm, MediaCCCDeUrlForm
from .recording import MediaCCCDe


class MediaCCCDeSettings(PermissionRequired, FormView):
    form_class = MediaCCCDeSettingsForm
    permission_required = "event.update_event"
    template_name = "pretalx_media_ccc_de/settings.html"

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action", "save")
        if action == "regenerate":
            messages.success(
                request, _("Looking for new talks – this may take a while.")
            )
            MediaCCCDe(request.event).fill_recording_urls()
            return super().post(request, *args, **kwargs)

        if action == "urls":
            form = MediaCCCDeUrlForm(request.POST, event=self.request.event)
            if not form.is_valid():
                messages.error(request, form.errors)
                return super().get(request, *args, **kwargs)
            form.save()
            messages.success(request, _("The URLs for this event have been changed."))
            return super().get(request, *args, **kwargs)

        return super().post(request, *args, **kwargs)

    def get_object(self):
        return self.request.event

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {"obj": self.request.event, "attribute_name": "settings", **kwargs}

    def get_context_data(self, *args, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["settings_buttons"] = [
            Button(name="action", value="save"),
            Button(
                name="action",
                value="regenerate",
                label=_("Check for new talks"),
                color="secondary",
            ),
        ]
        if self.request.event.current_schedule:
            kwargs["url_form"] = MediaCCCDeUrlForm(event=self.request.event)
            kwargs["url_form_buttons"] = [Button(name="action", value="urls")]
        else:
            kwargs["url_forms"] = []
        return kwargs
