from django.utils.translation import gettext_lazy as _

from app.models.interrogation import Interrogation
from wizard.views.json.base import WizardBase
from wizard.views.json.step.exceptions import RequiredFieldsError


class WizardStepExampleStep2(WizardBase):
    description = _("Step 2")
    breadcrumb = _("Step 2")

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
        # prepare the options to pre-select one (if there was one):
        select_interro_options = [
            {'id': 'select_interro_test_empty',
             'label': '-- Please choose --',
             'value': '-'}, ] + [
            {'id': 'select_interro_{}'.format(interro.pk),
             'label': interro.modele.description,
             'value': interro.pk}
            for interro in Interrogation.objects.filter(user=request.user)]
        data_step = data.get(wz_user_step.step, {})
        id_name_default = ''
        if data_step:
            id_name_default = data_step.get('id_name', _("Default value"))
            id_select_interro = data_step.get('id_select_interro')
            if id_select_interro:
                for option in select_interro_options:
                    if option['value'] == id_select_interro:
                        option['selected'] = True
        return [
            {'type': 'text',
             'data': [{'type': 'title_2',
                       'content': _("Step 2")}]
             },

            {'type': 'fieldset',
             'data': {
                 'id': '',
                 'content':
                     [{'type': 'legend',
                       'data': {'label': 'General information'},
                       },
                      {'type': 'input',
                       'data': {'id': 'id_name',
                                'name': 'id_name',
                                'input_type': 'text',
                                'label': 'Name',
                                'class': 'form-control ',
                                'max_length': '64',
                                'required': True,
                                'to_send': True,
                                'value': id_name_default}, },
                      {'id': 'select_interro_label',
                       'name': 'select_interro_label',
                       'type': 'select',
                       'data': {'class': 'form-control',
                                'id': 'id_select_interro',
                                'name': 'id_select_interro',
                                'label': _("Choose the interrogation"),
                                'options': select_interro_options,
                                'to_send': True}}, ],
             }},
            {'type': 'buttons',
             'data': {
                 'prev': 'step_1',
                 'next': 'step_3',
                 'cancel': True,
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
        if new_step not in ['step_1']:
            return self.incorrect_step_result()
        from wizard.models.wz_user_step import WzUserStep
        return True, WzUserStep.WZ_STEP_EXAMPLE_STEP_1, \
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
        if new_step not in ['draft', 'step_3']:
            return self.incorrect_step_result()

        post_vals = self.get_post_values(request)

        error_message = []
        error_fields = {}

        # data to save in database:
        db_data = {}

        # same code all time, possibility to generalize:
        name = post_vals.get('id_name')
        if not name:
            error_message.append(_("Enter a name"))
            error_fields['id_name'] = _("Enter a name")
        db_data['id_name'] = name

        # same code all time, possibility to generalize:
        try:
            id_select_interro = int(post_vals.get('id_select_interro'))
        except (TypeError, ValueError):
            id_select_interro = None
        if not id_select_interro:
            error_message.append(_("Select an interrogation"))
            error_fields['id_select_interro'] = _("Select an interrogation")
        db_data['id_select_interro'] = id_select_interro

        if error_message and new_step != 'draft':
            raise RequiredFieldsError(is_get=False, abnormal=False,
                                      title=_("Mandatory fields"),
                                      message=error_message,
                                      error_fields=error_fields)

        # local import to avoid circular reference
        from wizard.models.wz_user_step import WzUserStep
        return True, WzUserStep.WZ_STEP_EXAMPLE_STEP_3, \
            _("Step 2 done"), db_data, {'success': True, }
