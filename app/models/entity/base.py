from django.db import models, IntegrityError
from django.db.models.signals import pre_save
from django.dispatch import receiver

from app.models.address import Address
from app.models.address_type import AddressType
from app.models.base import BaseModel

from django.utils.translation import ugettext_lazy as _

from app.models.phone import Phone
from app.models.phone_type import PhoneType


class Entity(BaseModel):
    is_physical = models.BooleanField(default=True)

    def __str__(self):
        if hasattr(self, 'person'):
            return f'Base: {self.person.full_name()}'
        elif hasattr(self, 'entitiesgroup'):
            return f'Base: {self.entitiesgroup.to_str()}'
        return f'? {type(self).__name__}'


class EntityAddress(BaseModel):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE,
                               blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE,
                                blank=True, null=True)
    address_type = models.ForeignKey(AddressType, models.CASCADE,
                                     blank=True, null=True)

    class Meta:
        verbose_name = _("Entity address")
        verbose_name_plural = _("Entity addresses")


class EntityPhone(BaseModel):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE,
                               blank=True, null=True)
    phone = models.ForeignKey(Phone, on_delete=models.CASCADE,
                              blank=True, null=True)
    phone_type = models.ForeignKey(PhoneType, models.CASCADE,
                                   blank=True, null=True)

    class Meta:
        verbose_name = _("Entity phone")
        verbose_name_plural = _("Entity phones")


class EntityLink(BaseModel):
    # parent <> child
    L_PARENT_CHILD = 1
    L_PARENT = _("Parent")
    L_CHILD = _("Child")

    # husband <> wife
    L_HUSBAND_WIFE = 2
    L_HUSBAND = _("Husband")
    L_WIFE = _("Wife")

    # teacher <> student
    L_TEACHER_LEARNER = 3
    L_TEACHER = _("Teacher")
    L_LEARNER = _("Learner")

    # group of learners <> learners
    L_GROUP_OF_LEARNERS_LEARNER = 4
    L_GROUP_OF_LEARNERS = _("Group of learners")

    LINKS = {
        L_PARENT_CHILD: {'src': L_PARENT,
                         'dst': L_CHILD},
        L_HUSBAND_WIFE: {'src': L_HUSBAND,
                         'dst': L_WIFE},
        L_TEACHER_LEARNER: {'src': L_TEACHER,
                            'dst': L_LEARNER},
        L_GROUP_OF_LEARNERS_LEARNER: {'src': L_GROUP_OF_LEARNERS,
                                      'dst': L_LEARNER},
    }

    src = models.ForeignKey(Entity, on_delete=models.CASCADE,
                            related_name='src_tmp', blank=True, null=True)
    dst = models.ForeignKey(Entity, on_delete=models.CASCADE,
                            related_name='dst_tmp', blank=True, null=True)
    link_type = models.IntegerField(choices=[
        (a, '{} <> {}'.format(b['src'], b['dst']))
        for a, b in list(LINKS.items())],
        default=L_TEACHER_LEARNER)

    def __str__(self):
        rel = self.LINKS[self.link_type]
        return f"{self.pk} - " \
               f"{self.src} ({rel['src']}) > " \
               f"{self.dst} ({rel['dst']})"

    class Meta:
        verbose_name = _('Entity link')
        verbose_name_plural = _('Entity links')


@receiver(pre_save, sender=EntityLink)
def entity_link_pre_save(instance, *args, **kwargs):
    if EntityLink.objects.filter(src=instance.dst, dst=instance.src,
                                 link_type=instance.link_type).count() > 0:
        raise IntegrityError(_("There's already an opposite link like that"))
    return instance

