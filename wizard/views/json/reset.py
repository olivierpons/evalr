from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import generic

from wizard.models.wz_user_step import WzUserStep


class WizardJsonResetView(LoginRequiredMixin, generic.View):
    # override http_method_names = other methods return method_not_allowed()
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        # accept only this hard-coded value to reset the wizard:
        ok_to_reset = request.POST.get('reset')
        if ok_to_reset is None:  # hack
            return JsonResponse(False, safe=False)

        # when client gets "true", just reload the page and tada! new state:
        WzUserStep.objects.filter(user=request.user).delete()
        return JsonResponse(True, safe=False)