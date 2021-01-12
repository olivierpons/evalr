from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models.base import BaseModel


class DocumentState(BaseModel):
    EXPIRED = 1
    STR_EXPIRED = _("Expired")

    STATES = {
        EXPIRED: STR_EXPIRED,
    }
    state_previous = models.ForeignKey('self', default=None, blank=True,
                                       null=True, on_delete=models.CASCADE)
    state = models.PositiveIntegerField(choices=STATES.items(),
                                        default=None, blank=True, null=True)

    def str_previous(self):
        if self.state_previous is None:
            return _("no previous")
        return self.state_previous.str_current()

    def str_current(self):
        if self.state is None:
            return _("no current")
        return f'{DocumentState.STATES[self.state]}'

    def full_chain(self):
        result = f'-> {self.str_current()}'
        state_tmp_previous = self.state_previous
        while state_tmp_previous is not None:
            result = f'-> {state_tmp_previous.str_current()} {result}'
            state_tmp_previous = state_tmp_previous.state_previous
        return result.strip()

    def __str__(self):
        return f'({self.str_previous()} -> {self.str_current()})'

    class Meta:
        order_with_respect_to = 'state_previous'
