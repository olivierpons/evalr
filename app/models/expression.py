import uuid
from os import path, makedirs
from os.path import abspath, join

from django.core.files import File
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.db import models
from app.models.generic import BaseModel
from evalr.settings import MEDIA_ROOT
from .categorie import CategoriesGroup
from .voix import Voix

"""
/*
SELECT *
FROM app_mot
WHERE to_tsvector('french', texte) @@ to_tsquery('french', 'ouvrir');

CREATE INDEX app_mot_texte_idx
ON app_mot USING gin(to_tsvector('french', texte));

SELECT * FROM app_mot limit 2;

SELECT unaccent('èéêë');

CREATE INDEX app_mot_idx ON app_mot USING gist(texte);

*/
"""


class Expression(BaseModel):
    categories_groups = models.ManyToManyField(CategoriesGroup, blank=True,
                                               through='MotGroupeCategories',
                                               symmetrical=False,
                                               related_name='mot')
    voices = models.ManyToManyField(Voix, blank=True,
                                    through='ExpressionVoice',
                                    symmetrical=False,
                                    related_name='mot')
    generate_voice = models.BooleanField(default=True,
                                         verbose_name=_("Generate if no file"))
    generate_voice_language = models.CharField(max_length=8, blank=True,
                                               default=None, null=True,
                                               verbose_name=_("Language"))
    texte = models.CharField(max_length=150)
    exemple = models.CharField(max_length=150, blank=True, default=None,
                               null=True)
    reference = models.CharField(max_length=200, blank=True, default=None,
                                 null=True)
    important = models.BooleanField(default=False, blank=False, null=False,
                                    verbose_name=_("Important"))

    def get_voices(self, user):
        result = self.voices.all()
        if len(result):
            return result
        if not self.generate_voice:
            return []
        # region - Google Text to Speech generation -
        from gtts import gTTS
        nom = f'{self.pk}-{self.texte}.mp3'
        nom = str(uuid.uuid5(uuid.NAMESPACE_OID, nom))

        # Ex: dst = "play/bea536a0/089c/51a3/8c0e/beeb00f2a45b.mp3"
        dst = 'play/generated/'+'/'.join(nom.split('-'))

        # Ex: "C:\Users\...\play\bea536a0\089c\51a3\8c0e\beeb00f2a45b.mp3"
        dst_full = abspath(join(MEDIA_ROOT, dst))

        # Ex: "C:\Users\...\play\bea536a0\089c\51a3\8c0e"
        dst_base = path.dirname(dst_full)
        if not path.exists(dst_base):
            makedirs(dst_base)

        tts = gTTS(self.texte, lang=self.generate_voice_language or 'en')
        tts.save(dst_full)
        voice = Voix.objects.create(user=user)
        voice.description = _("{} (generated with gTTS)").format(self.texte)
        f = open(dst_full, mode='rb')
        voice.fichier_audio.save(dst_full, File(f))
        voice.save()
        ExpressionVoice.objects.create(mot=self, voix=voice).save()
        # endregion
        return self.voices.all()

    def expression_with_categories(self):
        categories_groups = self.categories_groups.all()
        d = zip(*[c.description.split() for c in categories_groups])
        b = []
        for a in d:
            if len(set(a)) == 1:
                b.append(set(a).pop())
            else:
                break
        a = ' '.join(b).strip()
        b = [' {}{}'.format(
            b.description[len(a):],
            ' "{}"'.format(b.exemple) if b.exemple else '').strip()
             for b in categories_groups]
        if len(b) > 2:
            b = ' ({}) - '.format(
                ', '.join(['<br/>&nbsp;&nbsp;&nbsp;&nbsp;- {}'.format(c)
                           for c in b]))
        elif len(b):
            b = ' {} - '.format(b[0])
        else:
            b = ''
        return format_html('{}{}{}'.format(a, b, self.texte).strip())
    expression_with_categories.short_description = _("Description")
    expression_with_categories.allow_tags = True
    # mot_avec_categories.admin_order_field = 'groupes__description'

    def __str__(self):
        return _('{}').format(self.texte)


class MotGroupeCategories(models.Model):
    expression = models.ForeignKey(Expression, blank=False,
                                   on_delete=models.CASCADE)
    group_categories = models.ForeignKey(CategoriesGroup, blank=False,
                                         on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {}'.format(self.expression.texte,
                                self.group_categories.description)

    class Meta:
        verbose_name = _("Expression: group of categories")
        verbose_name_plural = _("Expression: groups of categories")


class ExpressionVoice(models.Model):
    expression = models.ForeignKey(Expression, blank=False,
                                   on_delete=models.CASCADE)
    voix = models.ForeignKey(Voix, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.voix)

    class Meta:
        verbose_name = _("Expression voice")
        verbose_name_plural = _("Expression voices")


class GroupExpressions(models.Model):
    description = models.CharField(max_length=150)
    expressions = models.ManyToManyField(Expression, blank=True)

    class Meta:
        verbose_name = _('Expressions group')
        verbose_name_plural = _('Expressions groups')
        ordering = ['description']

    def __str__(self):
        a = '/'.join([
            str(m.texte)
            for m in self.expressions.all().order_by('date_last_modif')
            if m.important])
        a = (a[:a.find('/', 95)] + '...') if len(a) > 90 else a
        return '{}{}'.format(self.description, ' ({})'.format(a if a else ''))
