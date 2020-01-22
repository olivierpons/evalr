from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from app.models.entity.entities_group import EntitiesGroup
from wizard.views.json.base import WizardBase
from wizard.views.json.step.exceptions import RequiredFieldsError


class WizardStepNewLearnersGroupStep1(WizardBase):
    title = _("Wizard - New learners group")
    description = _("Name / how many?")
    breadcrumb = description

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
        str_datetime = now().strftime('%d-%m-%Y, %H:%M:%S')
        id_name_default = _(f"{str_datetime} - Group of learners")
        select_nb_learners = [
            {'id': 'select_nb_learners_empty',
             'label': '-- Please choose --',
             'value': '-'}, ] + [
            {'id': f'select_nb_learners_{i}',
             'label': str(i),
             'value': i} for i in range(100)
        ]

        # restore saved data
        data_step = data.get(wz_user_step.step, {})
        if data_step:
            id_name_default = data_step.get('name', id_name_default)
            id_select_nb_learners = data_step.get('nb_learners')
            if id_select_nb_learners:
                for option in select_nb_learners:
                    if option['value'] == id_select_nb_learners:
                        option['selected'] = True
        return [
            {'type': 'text',
             'line_break': False,
             'data': [
                 {'type': 'title_2',
                  'content': WizardStepNewLearnersGroupStep1.description},
             ]},
            {'type': 'fieldset',
             'data': {
                 'id': '',
                 'content':
                     [{'type': 'input',
                       'data': {'id': 'id_name',
                                'name': 'id_name',
                                'input_type': 'text',
                                'label': _("Name of the group"),
                                'class': 'form-control ',
                                'max_length': '64',
                                'required': True,
                                'to_send': True,
                                'value': id_name_default}, },
                      {'id': 'select_nb_learners_label',
                       'name': 'select_nb_learners_label',
                       'type': 'select',
                       'data': {'class': 'form-control',
                                'id': 'id_select_nb_learners',
                                'name': 'id_select_nb_learners',
                                'label': _("Number of learners"),
                                'options': select_nb_learners,
                                'to_send': True}}, ],
             }},
            {'type': 'buttons',
             'data': {'prev': '',
                      'next': 'step_2',
                      'cancel': True, }}
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
        # should never call back here: it's the first step!
        return self.incorrect_step_result()

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
        if new_step not in ['draft', 'step_2']:
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
        else:
            try:
                EntitiesGroup.objects.get(name__exact=name)
                # found = problem!
                raise RequiredFieldsError(
                    is_get=False, abnormal=False,
                    title=_("Name not unique"),
                    message=_("A group like this already exists"),
                    error_fields={
                        'id_name': _("Name is already taken, "
                                     "please change the name of the group")})
            except EntitiesGroup.DoesNotExist:
                pass
        db_data['name'] = name

        # same code all time, possibility to generalize:
        error = None
        try:
            id_select_nb_learners = int(post_vals.get('id_select_nb_learners'))
            if not (1 <= id_select_nb_learners <= 30):
                error = _("The number of learners must be > 0 and <= 30")
        except (TypeError, ValueError):
            id_select_nb_learners = None
        if not id_select_nb_learners:
            error = _("Select a number")

        if error is not None:
            error_message.append(error)
            error_fields['id_select_nb_learners'] = error

        db_data['nb_learners'] = id_select_nb_learners

        if error_message and new_step != 'draft':
            raise RequiredFieldsError(is_get=False, abnormal=False,
                                      title=_("Mandatory fields"),
                                      message=error_message,
                                      error_fields=error_fields)

        # local import to avoid circular reference
        from wizard.models.wz_user_step import WzUserStep
        return True, WzUserStep.WZ_STEP_NEW_LEARNERS_GROUP_STEP_2, \
            str(_('Name: {}, ({} learner(s))').format(name,
                                                      id_select_nb_learners)), \
            db_data, {'success': True, }
