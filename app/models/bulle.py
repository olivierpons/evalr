from colorful.fields import RGBColorField
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.utils import html


class Bulle(models.Model):
    description = models.CharField(max_length=150)
    color = RGBColorField()
    contour = RGBColorField(null=True)

    def to_html(self):
        if not self.description:
            d = ''
        else:
            d = ' title="{}" '.format(html.escape(self.description))
        if not self.contour:
            c = ''
        else:
            c = ' outline:solid 1px {};'.format(self.contour)
        return '<div style="' \
               'display: inline-block; width: 10px; height:10px; {} ' \
               'background-color: {}"{}>'\
               '</div>'.format(c, self.color, d)

    def __str__(self):
        return _('{} - {} ({})').format(self.pk,
                                        self.description,
                                        self.color)


class GroupeBulles(models.Model):
    description = models.CharField(max_length=150)
    bulles = models.ManyToManyField(Bulle, blank=True,
                                    symmetrical=False,
                                    through='GroupeBulle',
                                    through_fields=('groupe', 'bulle'))

    def bulles_html(self):
        return ' '.join([c.to_html() for c in self.bulles.all()])

    def __str__(self):
        return _('{} - {}').format(self.pk, self.description)

    class Meta:
        verbose_name = _("Group of bubbles")
        verbose_name_plural = _("Bubbles: groups of bubbles")


class GroupeBulle(models.Model):
    groupe = models.ForeignKey(GroupeBulles, verbose_name=_("Group"),
                               on_delete=models.CASCADE)
    bulle = models.ForeignKey(Bulle, verbose_name=_("Bubble"),
                              on_delete=models.CASCADE)

    def __str__(self):
        return _('{} / {}').format(self.groupe, self.bulle)

