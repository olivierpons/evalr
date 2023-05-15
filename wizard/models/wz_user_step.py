from heapq import merge
from itertools import cycle

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from wizard.views.json.step.example.step_1 import WizardStepExampleStep1
from wizard.views.json.step.example.step_2 import WizardStepExampleStep2
from wizard.views.json.step.example.step_3 import WizardStepExampleStep3
from wizard.views.json.step.new_exam.step_1 import WizardStepNewExamStep1
from wizard.views.json.step.new_exam.step_2 import WizardStepNewExamStep2
from wizard.views.json.step.new_exam.step_3 import WizardStepNewExamStep3
from wizard.views.json.step.new_learners_group.step_1 import \
    WizardStepNewLearnersGroupStep1
from wizard.views.json.step.new_learners_group.step_2 import \
    WizardStepNewLearnersGroupStep2
from wizard.views.json.step.new_learners_group.step_3 import \
    WizardStepNewLearnersGroupStep3
from wizard.views.json.step.new_learners_group.step_4 import \
    WizardStepNewLearnersGroupStep4


class WzUserStep(models.Model):

    WZ_UUID_EXAMPLE = 'wz-example'
    WZ_UUID_NEW_LEARNERS_GROUP = 'wz-new-learners-group'
    WZ_UUID_NEW_EXAM = 'wz-new-exam'
    WZ_TAB_UUID = [
        WZ_UUID_EXAMPLE,
        # other UUIDs come here for other wizards
        WZ_UUID_NEW_LEARNERS_GROUP,
        WZ_UUID_NEW_EXAM,
    ]

    WZ_DEFAULT_TITLE = _("Wizard")

    """
    ! Space is important in the following indexes:
      - only the first characters *until* a space ARE SAVED in the model
      - added description + spaces are for dump and debug reasons, do the same!
    """
    WZ_STEP_EXAMPLE_STEP_1 = 'spl-000 STEP_1'
    WZ_STEP_EXAMPLE_STEP_2 = 'spl-010 STEP_2'
    WZ_STEP_EXAMPLE_STEP_3 = 'spl-020 STEP_3'

    WZ_STEP_NEW_LEARNERS_GROUP_STEP_1 = 'nlg-000 STEP_1'
    WZ_STEP_NEW_LEARNERS_GROUP_STEP_2 = 'nlg-010 STEP_2'
    WZ_STEP_NEW_LEARNERS_GROUP_STEP_3 = 'nlg-020 STEP_3'
    WZ_STEP_NEW_LEARNERS_GROUP_STEP_4 = 'nlg-020 STEP_4'

    WZ_STEP_NEW_EXAM_TEMPLATE_STEP_1 = 'nxt-000 STEP_1'
    WZ_STEP_NEW_EXAM_TEMPLATE_STEP_2 = 'nxt-010 STEP_2'
    WZ_STEP_NEW_EXAM_TEMPLATE_STEP_3 = 'nxt-020 STEP_3'

    TAB_WZ_STEP = {
        # -------------------------------------------------------------
        # Wizard Example:
        WZ_UUID_EXAMPLE: {
            WZ_STEP_EXAMPLE_STEP_1: WizardStepExampleStep1,
            WZ_STEP_EXAMPLE_STEP_2: WizardStepExampleStep2,
            WZ_STEP_EXAMPLE_STEP_3: WizardStepExampleStep3,
        },
        # -------------------------------------------------------------
        # Other Wizard declaration could come here, like the one before.
        WZ_UUID_NEW_LEARNERS_GROUP: {
            WZ_STEP_NEW_LEARNERS_GROUP_STEP_1: WizardStepNewLearnersGroupStep1,
            WZ_STEP_NEW_LEARNERS_GROUP_STEP_2: WizardStepNewLearnersGroupStep2,
            WZ_STEP_NEW_LEARNERS_GROUP_STEP_3: WizardStepNewLearnersGroupStep3,
            WZ_STEP_NEW_LEARNERS_GROUP_STEP_4: WizardStepNewLearnersGroupStep4,
        },
        WZ_UUID_NEW_EXAM: {
            WZ_STEP_NEW_EXAM_TEMPLATE_STEP_1: WizardStepNewExamStep1,
            WZ_STEP_NEW_EXAM_TEMPLATE_STEP_2: WizardStepNewExamStep2,
            WZ_STEP_NEW_EXAM_TEMPLATE_STEP_3: WizardStepNewExamStep3,
        },
    }
    # ----------------------------------------------------------------------

    date_creation = models.DateTimeField(auto_now_add=True,
                                         verbose_name=_("Created"))
    date_last_modif = models.DateTimeField(auto_now=True,
                                           verbose_name=_("Last changed"))
    user = models.ForeignKey(User, default=None, null=True, blank=True,
                             on_delete=models.CASCADE)

    uuid_reference = models.CharField(
        max_length=200,
        choices=[(idx, b) for idx, b in enumerate(WZ_TAB_UUID)],
        default=WZ_TAB_UUID)

    uuid = models.CharField(max_length=200, default=None)

    step = models.CharField(
        max_length=200,
        # merge all WZ_STEP_XXX whatever the uuid is, to store only the step:
        # k2.split(' ')[0] = 'spl-000 STEP_1' becomes 'a000'
        # hack because of Python3 read here on stackoverflow:
        # /questions/13905741/accessing-class-variables-
        # from-a-list-comprehension-in-the-class-definition
        choices=sorted([a for a in merge(*[[
            (k2, '{} - {}'.format(k2.split(' ')[0].strip(),
                                  TAB_WZ_STEP[k1][k2]().description))
            for k2 in TAB_WZ_STEP[k1]]
            for k1, TAB_WZ_STEP in zip(TAB_WZ_STEP, cycle((TAB_WZ_STEP,)))])]),
        blank=True, null=True, default=None)
    data = models.TextField(default=None, blank=True, null=True, )

    def __str__(self):
        uuid = self.uuid_reference
        if not uuid or uuid not in self.TAB_WZ_STEP:
            description = _("? Unknown uuid: {}").format(uuid or '?')
        elif self.step in self.TAB_WZ_STEP[uuid]:
            description = self.TAB_WZ_STEP[uuid][self.step]().description
        else:
            description = _("? Unknown step: {}/{}").format(uuid, self.step)
        return '{} - {}/{} - {}'.format(str(self.user),
                                        self.uuid, self.step, description)
