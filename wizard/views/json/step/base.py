import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic


class WizardJsonStepBase(LoginRequiredMixin, generic.View):
    # override http_method_names = other methods return method_not_allowed()
    http_method_names = ['get', 'post']

    # static values
    tab = None
    uuid = None

    @staticmethod
    def initialize_uuid(**kwargs):
        uuid = kwargs.get('uuid')
        from wizard.models.wz_user_step import WzUserStep
        if uuid in WzUserStep.TAB_WZ_STEP:
            WizardJsonStepBase.uuid = uuid
            WizardJsonStepBase.tab = WzUserStep.TAB_WZ_STEP.get(uuid)
        else:
            WizardJsonStepBase.uuid = None
            WizardJsonStepBase.tab = None
        return WizardJsonStepBase.uuid, WizardJsonStepBase.tab

    @staticmethod
    def breadcrumb_pop_until(data, step):
        # change breadcrumb
        breadcrumb = data.get('breadcrumb', [])
        while len(breadcrumb):
            if breadcrumb[-1]['step'] == step:
                breadcrumb.pop()  # remove this step too (we're on it!)
                break
            breadcrumb.pop()
        return breadcrumb

    @staticmethod
    def goto_step(request, step, **kwargs):
        """
        Method separated so it can be directly called.
        In case of unrecoverable errors, we can force to go to a specific step.

        Args:
            request: the request
            step: the step to go to
            **kwargs: other arguments (company and uuid amongst others)

        Returns:
            True or False (False should never happen)
        """
        uuid, tab = WizardJsonStepBase.initialize_uuid(**kwargs)
        if step is None or step not in tab:  # should never happen
            return False

        # ! get_step() is in the child class WizardJsonStepView:
        # here create custom uuid to look in the database: format is
        # "[uuid]_[company]" so there's one unique wizard per company:
        from wizard.views.json.step.view import WizardJsonStepView
        wz_user_step, created, instance_class_step, data = \
            WizardJsonStepView.get_step(
                request,
                lambda _uuid: '{}_{}'.format(_uuid, kwargs['company']))

        # change user step
        wz_user_step.step = step

        data['breadcrumb'] = WizardJsonStepBase.breadcrumb_pop_until(data, step)
        wz_user_step.data = json.dumps(data)
        wz_user_step.save()
        # when client gets "true", just reload the page and tada! new step:
        return True

    @staticmethod
    def delete_steps(request, steps, **kwargs):
        """
        Delete all steps (when there's a critical error and we want to force
        the user to go back to a specific step).

        Args:
            request: the request
            steps: all the steps to remove
            **kwargs: other arguments (company and uuid amongst others)

        Returns:
            void
        """
        from wizard.models.wz_user_step import WzUserStep
        try:
            wus = WzUserStep.objects.get(user=request.user,
                                         uuid=kwargs.get('uuid'))
        except WzUserStep.DoesNotExist:
            return
        data = json.loads(wus.data) if wus.data else {}
        for step in steps:
            if data.get(step):
                del data[step]
        wus.data = json.dumps(data)
        wus.save()
