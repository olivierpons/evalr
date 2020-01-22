import platform

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models
from datetime import date
from os.path import basename, splitext, abspath, join

from pydub import AudioSegment

from evalr.settings import BASE_DIR
from app.models.generic import BaseModel


class AudioSegmentCustom(AudioSegment):

    def _spawn(self, data, overrides=None):
        # Question posée ici car problème en essayant de faire de l'héritage
        # http://stackoverflow.com/questions/37098835/how-to-force-to-a-class
        # la solution est de copier coller le code d'origine, et de renvoyer
        # "proprement" l'object construit via la classe en cours soit :
        # self.__class__() -> voir le "return" en fin de fonction:
        if overrides is None:
            overrides = {}
        if isinstance(data, list):
            data = b''.join(data)

        # accept file-like objects
        if hasattr(data, 'read'):
            if hasattr(data, 'seek'):
                data.seek(0)
            data = data.read()

        metadata = {
            'sample_width': self.sample_width,
            'frame_rate': self.frame_rate,
            'frame_width': self.frame_width,
            'channels': self.channels
        }
        metadata.update(overrides)
        return self.__class__(data=data, metadata=metadata)

    def fade_override(self, seg, fade_len=100):
        print('fade_override: fade_len={}'.format(fade_len))
        seg1, seg2 = AudioSegment._sync(self, seg)  # mettre les config max.
        final = seg1[:-fade_len]
        a_fin = seg1[-fade_len:].fade(to_gain=-120, start=0, end=float('inf'))
        a_fin *= seg2[:fade_len]
        return (final + a_fin) + seg2[fade_len:]


class Voix(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=150)
    fichier_audio = models.FileField()

    @staticmethod
    def ffmpeg_exec_path():
        if platform.system() != 'Windows':
            # return 'ffmpeg'
            return 'avconv'
        return abspath(join(BASE_DIR,
                            'windows_binaries/'
                            'libav-x86_64-w64-mingw32-20160507/usr/bin/avconv'))
        # 'ffmpeg-20151208-git-ff6dd58-win64-shared/'
        # 'bin/ffmpeg'))

    @staticmethod
    def yyyy_mm_dd():
        d = date.today()
        return '-'.join([str(d.year), '%02d' % d.month, '%02d' % d.day])

    @staticmethod
    def nom_mp3(nom_fichier, supplement=None):
        return '{}{}.mp3'.format(
            splitext(basename(nom_fichier))[0],
            "-%02d" % int(supplement) if supplement else u'')

    fusion_avec_suivant = models.ForeignKey('Fusion', null=True, blank=True,
                                            on_delete=models.CASCADE)

    def __str__(self):
        return _('{}, n°{}').format(self.description, self.pk)

    class Meta:
        verbose_name = _('Voice')
        verbose_name_plural = _('Voices')
        ordering = ['user__last_name', 'user__first_name', 'description', 'pk']


class Fusion(BaseModel):
    description = models.CharField(max_length=250)
    crossfade_length = models.IntegerField(blank=True, null=True, default=300)

    def __str__(self):
        return _('{} ({} ms)').format(self.description, self.crossfade_length)

    class Meta:
        verbose_name = _("Voice: merge")
        verbose_name_plural = _("Voice: merges")
