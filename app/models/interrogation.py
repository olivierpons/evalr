from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models

from app.models.bulle import GroupeBulles
from app.models.entity.person import Person
from app.models.generic import BaseModel
from app.models.modele import ModeleInterrogation

"""
Interrogation est composée :
- de phrases construites via ModeleInterrogation
- ces phrases sont uniques avec les mots sont choisis via ModeleInterrogation
- donc pour chaque phrase de Interrogation, il y a les mots uniques qui vont
  avec et qui sont classés dans l'ordre de la phrase
Au final :

Interrogation -+-> InterrogationPhrase -+-> InterrogationPhraseMot
               |                        +-> InterrogationPhraseMot
               |                        +-> ...
               |
               +-> InterrogationPhrase -+-> InterrogationPhraseMot
               |                        +-> ...
               +-> ...
"""


class Interrogation(BaseModel):
    groupe_bulles = models.ForeignKey(GroupeBulles, blank=True,
                                      default=None, null=True,
                                      on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name=_('Creator'),
                             on_delete=models.CASCADE)
    description = models.CharField(max_length=150)
    modele = models.ForeignKey(ModeleInterrogation,
                               verbose_name=_("Interrogation template"),
                               on_delete=models.CASCADE)
    persons = models.ManyToManyField(Person, blank=True,
                                     verbose_name=_("Persons"),
                                     through='InterrogationPerson',
                                     symmetrical=False,
                                     related_name='interrogations')

    def __str__(self):
        return _('{} - {}').format(self.pk, self.description)

    class Meta:
        verbose_name = _('Interrogation')
        verbose_name_plural = _('Interrogations')
        ordering = ['user__last_name', 'user__first_name', 'description', 'pk']


class InterrogationPerson(models.Model):
    interrogation = models.ForeignKey(Interrogation, blank=False,
                                      on_delete=models.CASCADE)
    person = models.ForeignKey(Person, blank=False,
                               on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.person)

    class Meta:
        verbose_name = _("Person interrogation")
        verbose_name_plural = _("Person interrogations")
