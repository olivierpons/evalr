# Tout ce qui concerne les Interrogations, y compris ModeleInterrogation

from django.utils.translation import gettext_lazy as _
from django.db import models

from app.models.bulle import GroupeBulles
from app.models.expression import GroupExpressions
from app.models.phrase import Phrase
from core.models.base import BaseModel


class ModeleInterrogation(models.Model):
    groupe_bulles = models.ForeignKey(GroupeBulles, blank=True,
                                      default=None, null=True,
                                      on_delete=models.CASCADE)
    description = models.CharField(max_length=150)
    phrases = models.ManyToManyField(Phrase, blank=True,
                                     through='ModeleInterrogationPhrase',
                                     symmetrical=False,
                                     related_name='phrase')
    groupes_mots = models.ManyToManyField(
            GroupExpressions, blank=True, symmetrical=False, related_name='mot',
            through='ModeleInterrogationGroupExpressions')
    df = models.FileField

    def __str__(self):
        return '{} - {}'.format(self.pk, self.description)

    class Meta:
        verbose_name = _("Exam template")
        verbose_name_plural = _("Exam templates")


class ModeleInterrogationGroupExpressions(models.Model):
    interrogation = models.ForeignKey(ModeleInterrogation, blank=False,
                                      on_delete=models.CASCADE)
    groupe_expressions = models.ForeignKey(GroupExpressions, blank=False,
                                           on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.groupe_expressions)

    class Meta:
        verbose_name = _("Exam template - group of expressions")
        verbose_name_plural = _("Exam template - groups of expressions")


class ModeleInterrogationPhrase(models.Model):
    interrogation = models.ForeignKey(ModeleInterrogation, blank=False,
                                      on_delete=models.CASCADE)
    phrase = models.ForeignKey(Phrase, blank=False,
                               on_delete=models.CASCADE)
    importance = models.IntegerField(blank=False, default=1)

    def __str__(self):
        return u'({}) - {}'.format(self.importance, self.phrase)

    class Meta:
        ordering = ['importance']
        verbose_name = _("Exam template - sentence")
        verbose_name_plural = _("Exam template - sentences")


class ModeleSession(BaseModel):
    description = models.CharField(max_length=150)
    total = models.IntegerField(blank=False, default=10,
                                verbose_name=_("Number of sentences"))
    max_duration = models.IntegerField(blank=False, default=None, null=True,
                                       verbose_name=_("Length (in minutes)"))

    def __str__(self):
        return _('{}').format(self.description)

    class Meta:
        verbose_name = _("Exam template - Session")
        verbose_name_plural = _("Exam template - Sessions")
        ordering = ['description', 'pk']
