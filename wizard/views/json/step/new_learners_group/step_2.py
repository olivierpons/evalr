from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, ungettext_lazy

from wizard.views.json.base import WizardBase
from wizard.views.json.step.exceptions import RequiredFieldsError


class WizardStepNewLearnersGroupStep2(WizardBase):
    title = _("Wizard - New learners group")
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
        from wizard.models.wz_user_step import WzUserStep
        data_step_1 = data.get(WzUserStep.WZ_STEP_NEW_LEARNERS_GROUP_STEP_1, {})
        nb_learners = data_step_1.get('nb_learners', -1)

        btn_prev_next = {'prev': 'step_1',
                         'next': 'step_3',
                         'cancel': True, }
        if 1 <= nb_learners <= 30:
            rows_title = [[self.make_cell('cell_title', val)
                           for val in ['N.',
                                       _("Email"),
                                       _("First name"), _("Last name"), ]]]

            def make_input_cell(input_id, input_type, value):
                return self.make_cell('cell',
                                      {'type': 'input',
                                       'data': {'id': f'{input_id}',
                                                'name': f'{input_id}',
                                                'input_type': input_type,
                                                'class': 'form-control ',
                                                'max_length': '64',
                                                'required': True,
                                                'to_send': True,
                                                'value': value or ''}, },)
            rows = []
            data_step = data.get(wz_user_step.step, {})
            for i in range(nb_learners):
                id_email = f'id_email_{i}'
                id_first_name = f'id_first_name_{i}'
                id_last_name = f'id_last_name_{i}'
                rows.append([])
                spaces = "&nbsp;"*8
                rows[i].append(self.make_cell('cell', f'{i + 1}{spaces}'))
                rows[i].append(make_input_cell(id_email, 'text',
                                               data_step.get(id_email)))
                rows[i].append(make_input_cell(id_first_name, 'text',
                                               data_step.get(id_first_name)))
                rows[i].append(make_input_cell(id_last_name, 'text',
                                               data_step.get(id_last_name)))
            table = {'type': 'table',
                     'data': {
                         # note : rows is an array
                         #    -> in rows there's an array of cells
                         #    -> in each cell there's an array of objects
                         #    -> array(rows) of array(cells) of array(objects)
                         # -> thus: 3 arrays [[[]]]:
                         'titles': rows_title,
                         'rows': rows}
                     }
        else:
            table = {'type': 'text',
                     'line_break': False,
                     'data': [
                         {'type': 'text',
                          'class': 'important warning',
                          'content': _("Incorrect number of learners.")},
                     ]}
            del btn_prev_next['next']
        return [
            {'type': 'text',
             'line_break': False,
             'data': [{'type': 'title_2',
                       'content': _("Step 2")},
                      {'type': 'title_4',
                       'content': _("Learners information")}, ]
             },

            {'type': 'fieldset',
             'data': {'id': '',
                      'content': [table, ],
                      }},
            {'type': 'buttons',
             'data': btn_prev_next}
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
        return True, WzUserStep.WZ_STEP_NEW_LEARNERS_GROUP_STEP_1, \
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

        error_message = []
        error_fields = {}
        post_vals = self.get_post_values(request)

        # data to save in database:
        db_data = {}
        from wizard.models.wz_user_step import WzUserStep
        data_step_1 = data.get(WzUserStep.WZ_STEP_NEW_LEARNERS_GROUP_STEP_1, {})
        nb_learners = data_step_1.get('nb_learners', -1)
        for i in range(nb_learners):
            id_email = f'id_email_{i}'
            id_first_name = f'id_first_name_{i}'
            id_last_name = f'id_last_name_{i}'
            email = post_vals.get(id_email)
            first_name = post_vals.get(id_first_name)
            last_name = post_vals.get(id_last_name)
            error = None
            if not email:
                error = _("Email can't be empty")
                error_message.append(error)
                error_fields[id_email] = error
            if not self.is_email(email):
                error = _("Invalid email")
                error_message.append(error)
                error_fields[id_email] = error
            if not first_name:
                error = _("First name can't be empty")
                error_message.append(error)
                error_fields[id_first_name] = error
            if not last_name:
                error = _("Last name can't be empty")
                error_message.append(error)
                error_fields[id_last_name] = error
            if error is None:
                db_data[id_email] = email
                db_data[id_first_name] = first_name
                db_data[id_last_name] = last_name
            if email and first_name and last_name:
                try:
                    u = User.objects.get(email=email)
                    if u.first_name != first_name or u.last_name != last_name:
                        error = _("Email already registered")
                        error_message.append(error)
                        error_fields[id_email] = error
                        if u.first_name != first_name:
                            error = _(f"First name different ({u.first_name})")
                            error_message.append(error)
                            error_fields[id_first_name] = error
                        else:
                            error = _(f"Last name different ({u.last_name})")
                            error_message.append(error)
                            error_fields[id_last_name] = error
                except User.MultipleObjectsReturned:
                    error = _("Email already registered (more than once!)")
                    error_message.append(error)
                    error_fields[id_email] = error
                except User.DoesNotExist:
                    pass

        if error_message and new_step != 'draft':
            raise RequiredFieldsError(is_get=False, abnormal=False,
                                      title=_("Mandatory fields"),
                                      message='',
                                      error_fields=error_fields)

        # local import to avoid circular reference
        from wizard.models.wz_user_step import WzUserStep
        return True, WzUserStep.WZ_STEP_NEW_LEARNERS_GROUP_STEP_3, \
            str(ungettext_lazy(
                str(_("1 learner entered")),
                _("Informations entered ({} learners)").format(nb_learners),
                nb_learners)), \
            db_data, {'success': True, }
