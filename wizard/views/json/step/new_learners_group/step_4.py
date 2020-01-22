import uuid

from django.contrib.auth.models import User
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from app.models.entity.base import EntityLink
from app.models.entity.entities_group import EntitiesGroup
from app.models.entity.entities_group_type import EntitiesGroupType
from app.models.entity.person import Person
from wizard.views.json.base import WizardBase


class WizardStepNewLearnersGroupStep4(WizardBase):
    title = _("Wizard - New learners group")
    description = _("Step 4")
    breadcrumb = _("Step 4")

    def get_content(self, request, wz_user_step, data, **kwargs):
        def _error_result(title, tab_errors):
            return [{'type': 'text',
                     'line_break': False,
                     'data': [{'type': 'title_2',
                               'content': _("Error")},
                              {'type': 'title_4',
                               'content': title},
                              {'type': 'text',
                               'line_break': True,
                               'content': tab_errors
                               }, ]
                     },
                    {'type': 'buttons',
                     'data': btn_prev_next}
                    ]
        """
        Args:
            request: the current request
            wz_user_step: current wz_user_step model
            data: all data gathered step after step
            **kwargs: other arguments (company and uuid amongst others)

        Returns:
            Object that should be returned as JSON
        """
        btn_prev_next = {'prev': 'step_3',
                         'cancel': True, }

        from wizard.models.wz_user_step import WzUserStep
        data_step_1 = data.get(WzUserStep.WZ_STEP_NEW_LEARNERS_GROUP_STEP_1, {})
        data_step_2 = data.get(WzUserStep.WZ_STEP_NEW_LEARNERS_GROUP_STEP_2, {})
        nb_learners = data_step_1.get('nb_learners', -1)
        name = data_step_1.get('name')
        if name and (1 <= nb_learners <= 30):
            rows_title = [[self.make_cell('cell_title', val)
                           for val in ['N.', _("Informations"), _("Result"), ]]]
            try:
                EntitiesGroup.objects.get(name__exact=name)
                # found = problem!
                return _error_result(
                    title=_("A group like this already exists"),
                    tab_errors=[_("Please change the name of the group"),
                                _("Click on corresponding step to change it.")])
            except EntitiesGroup.DoesNotExist:
                pass

            rows = []
            learners = []
            for i in range(nb_learners):
                email = data_step_2.get(f'id_email_{i}', '')
                first_name = data_step_2.get(f'id_first_name_{i}', '')
                last_name = data_step_2.get(f'id_last_name_{i}', '')
                username = Person.create_username(email, unique=False)
                try:
                    learners.append(
                        Person.objects.get(
                            user=User.objects.get(username=username,
                                                  email=email,
                                                  first_name=first_name,
                                                  last_name=last_name)))
                except User.DoesNotExist:  # User + Person to be created
                    learners.append(None)
                except Person.DoesNotExist:
                    return _error_result(
                        title=_("Email problem"),
                        tab_errors=[
                            _("Email: {} is already registered").format(email),
                            _("Please change it.")])

            with transaction.atomic():
                e_g_t, created = EntitiesGroupType.objects.get_or_create(
                    name=EntitiesGroupType.LEARNERS)
                e_g = EntitiesGroup.objects.create(name=name,
                                                   entities_group_type=e_g_t)
                for i in range(nb_learners):
                    email = data_step_2.get(f'id_email_{i}', '')
                    first_name = data_step_2.get(f'id_first_name_{i}', '')
                    last_name = data_step_2.get(f'id_last_name_{i}', '')
                    username = Person.create_username(email, unique=False)
                    if learners[i] is None:
                        user = User.objects.create(username=username,
                                                   email=email,
                                                   first_name=first_name,
                                                   last_name=last_name,
                                                   is_active=False)
                        # ! Person created through signal -> just read it:
                        p = user.person
                        p.confirmation_code = str(uuid.uuid4())  # rand. str
                        p.save()
                        message = f'-> {_("successfully created")}'
                    else:
                        p = learners[i]
                        message = '-> {}'.format(
                            _("account with this mail exists, "
                              "no action has been done")
                        )
                    EntityLink.objects.create(
                        src=e_g, dst=p,
                        link_type=EntityLink.L_GROUP_OF_LEARNERS_LEARNER)
                    sp = "&nbsp;" * 10
                    rows.append([])
                    rows[i].append(self.make_cell(
                        'cell', f'{i + 1}{sp}'))
                    rows[i].append(self.make_cell(
                        'cell', f'{email} / {first_name} {last_name} {sp}'))
                    rows[i].append(self.make_cell('cell', message))

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

        return [
            {'type': 'text',
             'line_break': False,
             'data': [
                 {'type': 'title_2',
                  'content': _("Success!")},
                 {'type': 'title_4',
                  'content': _(f'"{name}" has been successfully created')}, ]},
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
        if new_step not in ['step_3']:
            return self.incorrect_step_result()
        from wizard.models.wz_user_step import WzUserStep
        return True, WzUserStep.WZ_STEP_NEW_LEARNERS_GROUP_STEP_3, \
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
