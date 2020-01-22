from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from app.models.entity.person import Person
from .expression import Expression
from .generic import BaseModel
from .interrogation import Interrogation
from .modele import ModeleSession
from .phrase import Phrase


class PersonneSession(BaseModel):
    personne = models.ForeignKey(Person, verbose_name=_("Person"),
                                 on_delete=models.CASCADE)
    modele = models.ForeignKey(ModeleSession, verbose_name=_("Session ref."),
                               on_delete=models.CASCADE)
    interrogation = models.ForeignKey(Interrogation,
                                      verbose_name=_("Interro ref."),
                                      on_delete=models.CASCADE)
    phrases = models.ManyToManyField(Phrase, blank=True,
                                     through='PersonneSessionPhrase',
                                     symmetrical=False,
                                     related_name='session')

    def __str__(self):
        return _(u'N°{} : {} / {} ').format(
                self.pk, self.personne, self.modele.description)

    class Meta:
        verbose_name = _("Interrogation: session of a person")
        verbose_name_plural = _("Interrogation: sessions of a person")
        ordering = ['pk']


class PersonneSessionPhrase(BaseModel):
    """
    Les phrases construites pour cette session
    """
    ps = models.ForeignKey(PersonneSession, on_delete=models.CASCADE)
    phrase = models.ForeignKey(Phrase, on_delete=models.CASCADE)
    fichier_audio = models.FileField(default=None, blank=True, null=True)

    def __str__(self):
        return _('N°{} (session n°{} : {}) / {}').format(
                self.pk, self.ps.pk, str(self.ps.modele), self.phrase)


class PersonneSessionPhraseMot(BaseModel):
    """
    Les mots utilisés dans les phrases construites la session d'une personne
    Le mot sur lequel on a été interrogé
    """
    psp = models.ForeignKey(PersonneSessionPhrase, on_delete=models.CASCADE)
    mot = models.ForeignKey(Expression, on_delete=models.CASCADE)
    ordre = models.IntegerField(blank=False)

    ETAT_ATTENTE_CORRECTION = 1
    ETAT_CORRIGE = 2
    TAB_ETAT = {ETAT_ATTENTE_CORRECTION: _('To be done'),
                ETAT_CORRIGE: _('Done'), }
    etat = models.IntegerField(choices=[(a, b) for a, b in
                                        list(TAB_ETAT.items())],
                               default=ETAT_ATTENTE_CORRECTION)
    correcteur = models.ForeignKey(Person, default=None,
                                   blank=True, null=True,
                                   on_delete=models.CASCADE)
    date_correction = models.DateTimeField(default=timezone.now)
    est_valide = models.BooleanField(default=False, blank=False,
                                     verbose_name=_('Valid'))

    def __str__(self):
        return '({}) {}'.format(self.psp, self.mot.texte)

    class Meta:
        ordering = ['psp', 'mot__texte', 'ordre']
