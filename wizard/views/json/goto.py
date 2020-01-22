from django.http import JsonResponse

from wizard.views.json.step.base import WizardJsonStepBase


class WizardJsonGotoView(WizardJsonStepBase):

    # override http_method_names = other methods return method_not_allowed()
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        # accept only POST value 'step' (hard-coded) to reset the wizard:
        return JsonResponse(self.goto_step(request,
                                           request.POST.get('step'),
                                           **kwargs),
                            safe=False)
