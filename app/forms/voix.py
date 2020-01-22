
import os
import subprocess
import wave
from io import BytesIO
from os.path import abspath, join, isfile

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from evalr.settings import MEDIA_ROOT
from app.models.voix import Voix


class VoixForm(forms.ModelForm):

    def clean_fichier_audio(self):
        src = self.cleaned_data.get('fichier_audio', None)
        if src:
            # essayer de voir si ce qui arrive est juste un lien statique
            # URL qui pointe vers le fichier (ça arrive quand on est en
            # édition et qu'on avait envoyé un fichier)
            # (!) astuce : mode édition = pk pas null = if self.instance.pk...
            # nom = join(MEDIA_ROOT, src.name)
            # if self.instance.pk and isfile(nom):
            #     return src.name
            #
            # je garde le code au dessus au cas où mais comparer simplement
            # les types semble plus fiable : src.file est le champ Django
            # du modèle, si aucun upload, sinon de type BytesIO :
            if type(src.file) != BytesIO:
                return src.name
            if src.size > 40*1024*1024:
                raise ValidationError(_("File too big (limit: 40Mb)"))
            try:
                w = wave.open(src)
                w.close()
                p = Voix.ffmpeg_exec_path()
                dst_base = abspath(join(MEDIA_ROOT, Voix.yyyy_mm_dd()))
                if not os.path.exists(dst_base):
                    os.makedirs(dst_base)
                i = dst_total = 0
                while True:
                    dst_seul = Voix.nom_mp3(src.name, i)
                    if not isfile(dst_total):
                        break
                    i += 1
                if subprocess.call([
                   p, '-i', src.name,
                   '-loglevel', 'panic',  # panic = output que si erreur grave
                   '-y', '-codec:a', 'libmp3lame',
                   # '-qscale:a', '2', qscale = qualité
                   dst_total]):
                    raise ValidationError(_("File conversion error"))
                # Calcul du lien URL des upload
                return '/'.join([Voix.yyyy_mm_dd(), dst_seul])
            except wave.Error:
                raise ValidationError(_("File reading error"))
        else:
            raise ValidationError(_("File reading error"))

    class Meta:
        model = Voix
        fields = ['description', 'fichier_audio']
