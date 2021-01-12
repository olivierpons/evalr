from django.utils.translation import ugettext_lazy as _
from django.db import models

from core.models.base import BaseModel


class EntitiesGroupType(BaseModel):
    # constants that should be always present (use them via get_or_create())
    LEARNERS = _("Learners")

    name = models.CharField(max_length=200, default=_("(no type)"),
                            blank=True, null=True, )

    def __str__(self):
        return self.name if self.name is not None else _("(no name)")

    class Meta:
        verbose_name = _("Entities group type")
        verbose_name_plural = _("Entities group types")
