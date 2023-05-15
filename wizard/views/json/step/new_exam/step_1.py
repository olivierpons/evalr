from django.utils.translation import gettext_lazy as _, ngettext_lazy

from app.models.interrogation import Interrogation
from wizard.views.json.base import WizardBase
from wizard.views.json.step.exceptions import RequiredFieldsError


class WizardStepNewExamStep1(WizardBase):
    title = _("Wizard - New examination")
    description = _("Step 1")
    breadcrumb = _("Step 1")

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
        result = [{'type': 'text',
                   'line_break': False,
                   'data': [
                       {'type': 'title_2',
                        'content': _("Step 1")},
                       # {'type': 'title_4',
                       #  'content': _("New exam")},
                       # {'type': 'p',
                       #  'class': 'important warning',
                       #  'content': [
                       #      _("Sample")
                       #  ]},
                   ]}, ]
        total = Interrogation.objects.filter(user=request.user).count()
        if total:
            result.append({
                'type': 'text',
                'line_break': True,
                'data': [
                    {'type': 'p',
                     'line_break': False,  # line break *inside*, only here:
                     'content': [ngettext_lazy(
                         str(_("You have one template. "
                               "Do you want to use it?")),
                         str(_("You have {} templates. Do you want to use "
                               "one of them?")).format(total),
                         total), ]},
                    ' ']
            })
            result.append({
                'id': 'select_use_template',
                'name': 'select_use_template',
                'type': 'select_radio',
                'data': {'choices': [{'checked': True,
                                      'id': 'select_use_template_0',
                                      'name': 'select_use_template',
                                      'label': str(_("Yes")),
                                      'value': 1},
                                     {'checked': False,
                                      'id': 'select_choose_tab_1',
                                      'label': _("No"),
                                      'name': 'select_use_template',
                                      'value': -1}],
                         'class': 'select-vertical-align',
                         'to_send': True},
            },)
        else:
            # no total = no template
            result.append({
                'type': 'text',
                'line_break': True,
                'data': [
                    str(_("You have no template. Let's make one, it's easy."))
                ]
            })

        # finally, add buttons:
        result.append({'type': 'buttons', 'data': {'prev': '',
                                                   'next': 'step_2'}})
        return result

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
        if new_step not in ['step_2']:
            return self.incorrect_step_result()

        # data to save in database:
        db_data = None
        post_vals = self.get_post_values(request)

        error_message = []
        error_fields = {}
        # data to save in database:
        db_data = {}

        # same code all time, possibility to generalize:
        if Interrogation.objects.filter(user=request.user).count():
            try:
                yes = int(post_vals.get('select_use_template')) == 1
                db_data['use_existing_template'] = yes
                if yes:
                    summary = str(_("Use an existing template"))
                else:
                    summary = str(_("Create a new template"))
            except (TypeError, ValueError):  # hack
                error_message.append(_("Enter value"))
                error_fields['select_use_template'] = _("Enter value")
                summary = str(_("No value provided, enter a value."))

            if error_message and new_step != 'draft':
                raise RequiredFieldsError(is_get=False, abnormal=False,
                                          title=_("Mandatory fields"),
                                          message=error_message,
                                          error_fields=error_fields)
        else:
            summary = str(_("Create a new template"))

        # local import to avoid circular reference
        from wizard.models.wz_user_step import WzUserStep
        return True, WzUserStep.WZ_STEP_NEW_EXAM_TEMPLATE_STEP_2, \
            summary, db_data, {'success': True, }
