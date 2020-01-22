from django.utils.translation import ugettext_lazy as _

from wizard.views.json.base import WizardBase


class WizardStepNewLearnersGroupStep3(WizardBase):
    title = _("Wizard - New learners group")
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
        btn_prev_next = {'prev': 'step_2',
                         'next': 'step_3',
                         'cancel': True, }
        from wizard.models.wz_user_step import WzUserStep
        data_step_1 = data.get(WzUserStep.WZ_STEP_NEW_LEARNERS_GROUP_STEP_1, {})
        data_step_2 = data.get(WzUserStep.WZ_STEP_NEW_LEARNERS_GROUP_STEP_2, {})

        # region - table computation -
        nb_learners = data_step_1.get('nb_learners', -1)
        if 1 <= nb_learners <= 30:
            rows_title = [[self.make_cell('cell_title', val)
                           for val in ['N.',
                                       _("Email"),
                                       _("First name"), _("Last name"), ]]]

            rows = []
            for i in range(nb_learners):
                sp = "&nbsp;" * 10
                rows.append([])
                rows[i].append(self.make_cell('cell', f'{i + 1}{sp}'))
                rows[i].append(self.make_cell(
                    'cell', data_step_2.get(f'id_email_{i}', '')+sp))
                rows[i].append(self.make_cell(
                    'cell', data_step_2.get(f'id_first_name_{i}', '')+sp))
                rows[i].append(self.make_cell(
                    'cell', data_step_2.get(f'id_last_name_{i}', '')+sp))
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
                          'content': _("Incorrect data.")},
                     ]}
            del btn_prev_next['next']
        # endregion - table computation -

        return [
            {'type': 'text',
             'line_break': False,
             'data': [{'type': 'title_2',
                       'content': _("Step 3")},
                      {'type': 'title_4',
                       'line_break': False,
                       'content': [_("Summary"), " - ",
                                   {'type': 'text',
                                    'line_break': False,
                                    'data': {'type': 'text',
                                             'class': 'warning',
                                             'content': _("validation step")}},
                                   ]}, ]
             },
            {'type': 'text',
             'line_break': False,
             'data': {
                 'type': 'title_5',
                 'line_break': False,
                 'content': [{'type': 'text',
                              'data': {'type': 'text',
                                       'class': 'important',
                                       'content': f'{data_step_1["name"]}'}},
                             ]
             }},
            {'type': 'fieldset',
             'data': {'id': '',
                      'content': [table, ],
                      }},
            {'type': 'text',
             'line_break': False,
             'data': [{'type': 'p',
                       'line_break': True,
                       'class': 'important',
                       'content': ['', _("Click on \"Next\" "
                                         "to validate the group")]},
                      {'type': 'p',
                       'class': 'important warning',
                       'content': _("Make sure everything is ok "
                                    "before clicking \"Next\"")},
                      ]
             },
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
        if new_step not in ['step_2']:
            return self.incorrect_step_result()
        from wizard.models.wz_user_step import WzUserStep
        return True, WzUserStep.WZ_STEP_NEW_LEARNERS_GROUP_STEP_2, \
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
        # local import to avoid circular reference
        from wizard.models.wz_user_step import WzUserStep
        return True, WzUserStep.WZ_STEP_NEW_LEARNERS_GROUP_STEP_4, \
            str(_("Validation done")), None, {'success': True, }
