import json

from django.http import JsonResponse

from wizard.views.json.step.view import WizardJsonStepView


class WizardJsonCancelView(WizardJsonStepView):
    # override http_method_names = other methods return method_not_allowed()
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        # accept only this hard-coded value to cancel the current step:
        ok_to_cancel = request.POST.get('cancel')
        if ok_to_cancel is None:  # hack
            return JsonResponse(False, safe=False)

        # when client gets "true", just reload the page and tada! new state:
        # here create custom uuid to look in the database:
        # format is "[uuid]_[company]" so there's one unique wizard per company:
        wz_user_step, created, step_instance, data = self.get_step(
            request,
            lambda _uuid: '{}_{}'.format(_uuid, kwargs['company']))
        if not created:
            step = wz_user_step.step
            if data.get(step, {}).get('real') is not None:
                data[step]['draft'] = {}
                wz_user_step.data = json.dumps(data)
                wz_user_step.save()

        return JsonResponse(True, safe=False)
