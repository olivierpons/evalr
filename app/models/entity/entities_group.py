from django.utils.translation import ugettext_lazy as _
from django.db import models

from app.models.entity.base import Entity
from app.models.entity.entities_group_type import EntitiesGroupType


class EntitiesGroupManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_physical=False)


class EntitiesGroup(Entity):
    entities_group_type = models.ForeignKey(EntitiesGroupType,
                                            default=None, blank=True, null=True,
                                            on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default=_("(no name)"),
                            blank=True, null=True, )
    objects = EntitiesGroupManager()

    def save(self, *args, **kwargs):
        if kwargs.get('is_physical') is not None:
            kwargs.pop('is_physical')
        self.is_physical = False
        super().save(*args, **kwargs)

    def to_str(self):
        if self.entities_group_type is not None:
            g_t = str(self.entities_group_type)
        else:
            g_t = _("(no type)")
        name = self.name if self.name is not None else _("(no name)")
        return f'{g_t} - {name}'

    def __str__(self):
        return self.to_str()

    class Meta:
        verbose_name = _('Entities group')
        verbose_name_plural = _('Entities groups')
        ordering = ['entities_group_type__name', 'name',
                    'date_v_start', 'date_updated', 'date_creation', 'pk']
