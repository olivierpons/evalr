from django.utils.translation import ugettext_lazy as _

from wizard.views.json.base import WizardBase


class WizardStepExampleStep3(WizardBase):
    description = _("Step 3")
    breadcrumb = _("Step 3")

    def get_content(self, request, wz_user_step, data, **kwargs):
        """
        Args:
            request: the current request
            wz_user_step: current wz_user_step model
            data: all data gathered step after step
            **kwargs: other arguments (company and uuid amongst others)

        Returns:
            Object that should be returned as JSON
        """
        return [
            {'type': 'text',
             'data': [{'type': 'title_2',
                       'content': _("Step 3 - final sample")}]
             },
            {'type': 'buttons',
             'data': {
                 'prev': 'step_2',
                 'next': ''
             }}
        ]

    def set_prev_step(self, new_step, request, data, **kwargs):
        """
        Analyze parameters and if it's ok returns the previous step
        (*without modifying database*)

        Args:
            new_step: new_step (coming from user choice)
            request: the current request
            data: all data gathered step after step
            **kwargs: other arguments (company and uuid amongst others)

        Returns:
            5 values:
                - success: True or False if success,
                - new_user_step: New step (ignored if success == False)
                - breadcrumb_detail: (ignored here (= previous step))
                - db_data: None = ignored else data to write *for current step*
                - result: (ignored here -> return only {'success': True, } )
        """
        if new_step not in ['step_2']:
            return self.incorrect_step_result()
        from wizard.models.wz_user_step import WzUserStep
        return True, WzUserStep.WZ_STEP_EXAMPLE_STEP_2, \
            None, None, {'success': True, }

    def set_next_step(self, new_step, request, data, **kwargs):
        """
        Analyze parameters and if it's ok returns the next step
        (*without modifying database*)

        Args:
            new_step: new_step (coming from user choice)
            request: the current request
            data: all data gathered step after step
            **kwargs: other arguments (company and uuid amongst others)

        Returns:
            5 values:
                - success: True or False if success,
                - new_user_step: New step (ignored if success == False)
                - breadcrumb_detail: Detail to show (summary of choices done)
                - db_data: Data to remember into database (if any)
                - result: Object to JSON-encode for the AJAX result
        """
        return self.incorrect_step_result()
