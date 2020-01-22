from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from wizard.models.wz_user_step import WzUserStep


class WizardNewExamTemplateView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'new/wizard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Wizard")
        context['wz_uuid'] = WzUserStep.WZ_UUID_NEW_EXAM
        context['company'] = 'test-sample-company'
        return context

