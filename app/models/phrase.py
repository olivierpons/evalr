from django.utils.translation import ugettext_lazy as _
from django.db import models

from .categorie import CategoriesGroup


class Phrase(models.Model):
    description = models.CharField(max_length=200)
    exemple = models.CharField(max_length=150, blank=True, default=None,
                               null=True)
    categories_groups = models.ManyToManyField(
        CategoriesGroup, blank=True,
        through='PhraseGroupeCategories',
        symmetrical=False, related_name='phrase')
    duree_silence_debut = models.DecimalField(
        blank=True, max_digits=3, decimal_places=2,
        default=0.3, verbose_name=_('Silence length (start of the sentence)'))
    duree_silence_fin = models.DecimalField(
        blank=True, max_digits=3, decimal_places=2,
        default=0.3, verbose_name=_('Silence length (end of the sentence)'))

    def __str__(self):
        return _('{}').format(self.description)


class PhraseGroupeCategories(models.Model):
    ordre = models.IntegerField(blank=False, default=1)
    phrase = models.ForeignKey(Phrase, blank=False, on_delete=models.CASCADE)
    group_categories = models.ForeignKey(CategoriesGroup, blank=False,
                                         on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.group_categories.description)
        # don't display details, it's almost never needed:
        # return '{} / {}'.format(self.phrase,
        #                         self.group_categories.description)

    class Meta:
        ordering = ['ordre']
        verbose_name = _("Sentence: group of categories")
        verbose_name_plural = _("Sentence: groups of categories")
