from django.contrib.staticfiles import finders
from django.db import models
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from core.models.base import BaseModel


class Langue(BaseModel):
    nom = models.CharField(max_length=50)
    nom_local = models.CharField(max_length=50, default='')
    locale = models.CharField(max_length=5)  # (e.g. "fr")
    bidirectionnel = models.BooleanField(default=False)
    active = models.BooleanField(default=False)

    def url_drapeau(self):
        if not self.locale:
            return None
        # path codé en dur, ça ne devrait jamais changer :
        a = 'img/flags/flag-{}-s.png'.format(self.locale)
        # ! Astuce : finder de django :
        if not finders.find(a):
            return None
        return static(a)

    def __str__(self):
        return '{} / {}{}'.format(
            self.locale, self.nom, (_("- activated") if self.active else "")
        )

    class Meta(BaseModel.Meta):
        verbose_name_plural = _(u"Languages")
