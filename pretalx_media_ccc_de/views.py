from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from pretalx.common.mixins.views import PermissionRequired
from pretalx.submission.models import Submission

from .forms import MediaCCCDeSettingsForm, MediaCCCDeUrlForm
from .recording import MediaCCCDe


class MediaCCCDeSettings(PermissionRequired, FormView):
    form_class = MediaCCCDeSettingsForm
    permission_required = "orga.change_settings"
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

        if action.startswith("url"):
            code = action[len("url_") :]
            try:
                submission = request.event.submissions.get(code=code)
            except Submission.DoesNotExist:
                messages.error(request, _("Could not find this talk."))
                return super().get(request, *args, **kwargs)

            form = MediaCCCDeUrlForm(request.POST, submission=submission)
            if not form.is_valid():
                messages.error(request, form.errors)
                return super().get(request, *args, **kwargs)
            else:
                request.event.settings.set(
                    f"media_ccc_de_url_{submission.code}",
                    form.cleaned_data["media_ccc_de_url"],
                )
                messages.success(request, _("The URL for this talk was overridden."))
                return super().get(request, *args, **kwargs)

        return super().post(request, *args, **kwargs)

    def get_object(self):
        return self.request.event

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {"obj": self.request.event, "attribute_name": "settings", **kwargs}

    def get_context_data(self, *args, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["url_forms"] = [
            MediaCCCDeUrlForm(submission=slot.submission)
            for slot in self.request.event.current_schedule.talks.all()
            .filter(is_visible=True)
            .order_by("start")
        ]
        return kwargs
