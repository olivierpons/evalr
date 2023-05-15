import re
from django.utils.translation import gettext_lazy as _
from django.db import models


class Regle(models.Model):
    COMMENCE_PAR = 0
    SE_TERMINE_PAR = 1
    NE_COMMENCE_PAS_PAR = 2
    NE_SE_TERMINE_PAS_PAR = 3
    TAB_GROUPES = {
        COMMENCE_PAR: _("... starts with"),
        SE_TERMINE_PAR: _("... ends with"),
        NE_COMMENCE_PAS_PAR: _("... doesn't start with"),
        NE_SE_TERMINE_PAS_PAR: _("... doesn't end with"),
    }
    TAB_TESTS = {
        COMMENCE_PAR: '^{}{}{}.*',
        SE_TERMINE_PAR: '.*{}{}{}$',
        NE_COMMENCE_PAS_PAR: '^(?!{}{}{}).*',
        NE_SE_TERMINE_PAS_PAR: '.*(?!{}{}{})$',
    }
    description = models.CharField(max_length=200)
    exemple_src = models.CharField(max_length=150, blank=True, default=None,
                                   null=True)
    exemple_dst = models.CharField(max_length=150, blank=True, default=None,
                                   null=True)

    mot_courant_regle = models.IntegerField(
        choices=[(a, b) for a, b in list(TAB_GROUPES.items())],
        default=COMMENCE_PAR, verbose_name=_("Rule"))
    mot_courant_filtre = models.CharField(max_length=1250)
    mot_courant_filtre_est_lettre = models.BooleanField(
        default=False, blank=False,
        verbose_name=_("letters (un-checked) or words (checked)"),
        help_text=_("Ex.: letters: 'ùûüÿAE', words: 'un|des|les|ces'"))
    mot_courant_case_insensible = models.BooleanField(
        default=False, blank=False,
        verbose_name=_("Not case sensitive"), )

    mot_suivant_regle = models.IntegerField(
        choices=[(a, b) for a, b in list(TAB_GROUPES.items())],
        default=COMMENCE_PAR, verbose_name=_("Rule"))
    mot_suivant_filtre = models.CharField(max_length=1250)
    mot_suivant_filtre_est_lettre = models.BooleanField(
        default=False, blank=False,
        verbose_name=_("letters (un-checked) or words (checked)"),
        help_text=_("Ex.: letters: 'ùûüÿAE', words: 'un|des|les|ces'"))
    mot_suivant_case_insensible = models.BooleanField(
        default=False, blank=False,
        verbose_name=_("Not case sensitive"), )

    # from app.models.expression import Expression
    mot_remplacant = models.ForeignKey('app.Expression',
                                       blank=True, null=True,
                                       on_delete=models.CASCADE)

    def teste_filtre(self, regle, filtre, filtre_est_lettre, ignore_case, mot):
        (o, f) = ('[', ']') if not filtre_est_lettre else ('(', ')')
        rg = self.TAB_TESTS[regle].format(o, filtre, f)
        if ignore_case and re.match(rg, mot.texte, re.IGNORECASE):
            return True
        elif re.match(rg, mot.texte):
            return True
        return False

    def ok_with_mots(self, courant, suivant):
        if self.teste_filtre(self.mot_courant_regle,
                             self.mot_courant_filtre,
                             self.mot_courant_filtre_est_lettre,
                             self.mot_courant_case_insensible,
                             courant) and \
                self.teste_filtre(self.mot_suivant_regle,
                                  self.mot_suivant_filtre,
                                  self.mot_suivant_filtre_est_lettre,
                                  self.mot_suivant_case_insensible,
                                  suivant):
            return True
        return None

    def __str__(self):
        return _('{} ({} <> {})...').format(
            self.description, self.exemple_src, self.exemple_dst
        )

    class Meta:
        verbose_name = _("Rule")
        verbose_name_plural = _("Rules")

