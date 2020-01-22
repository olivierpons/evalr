import os
from os.path import splitext, basename

import magic
from django.conf.urls.static import static
from django.urls import reverse_lazy
from django.utils.dateformat import DateFormat
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.utils import timezone

from app.forms.generic.generic import UploadedFileHandler
from evalr import settings


class BaseModel(models.Model):
    date_creation = models.DateTimeField(auto_now_add=True,
                                         verbose_name=_('Date C.'))
    date_last_modif = models.DateTimeField(auto_now=True,
                                           verbose_name=_('Date M.'))

    date_v_start = models.DateTimeField(
        default=timezone.now,
        editable=True,
        verbose_name=_("V. start")
    )
    date_v_end = models.DateTimeField(
        default=None,
        null=True,
        editable=True,
        verbose_name=_("V. end"),
        blank=True
    )

    @staticmethod
    def format_date(value):
        if value:
            return DateFormat(value).format('d/m/Y, H:i')
        return _('Infinite')

    @staticmethod
    def str_clean(a, if_none='', sep='', max_len=30):
        if a is None:
            return if_none
        b = str(a)  # ! force to str()
        return '{}{}'.format(sep, b[:max_len] if len(b) > max_len else b)

    class Meta:
        abstract = True
        ordering = ['date_v_start']


class SharedModel(BaseModel):
    TYPE_PRIVATE = 1
    TYPE_ONLY_CLOSE = 2
    TYPE_EVERYBODY = 3
    TAB_TYPES = {
        TYPE_PRIVATE: _("Private"),
        TYPE_ONLY_CLOSE: _("Only close relationships"),
        TYPE_EVERYBODY: _("Everybody"),
    }
    type_relation = models.IntegerField(choices=[(a, b) for a, b in
                                                 list(TAB_TYPES.items())],
                                        default=TYPE_PRIVATE)

    class Meta:
        abstract = True


class BaseFileModel(BaseModel):
    upload_directory = ''

    def __init__(self, *args, **kwargs):
        if self.upload_directory != '':
            if not self.upload_directory.endswith('/'):
                self.upload_directory += '/'
        super(BaseFileModel, self).__init__(*args, **kwargs)

    # Generate dynamically a filename:
    def generate_filename(self, file_name):
        # nom: "bea536a0-089c-a45b.pdf"
        final_name = UploadedFileHandler.generate_filename(
            splitext(basename(file_name))[1])
        # Retour ex: "profiles/bea536a0/089c/a45b.pdf"
        return UploadedFileHandler.get_url(final_name, self.upload_directory)

    description = models.CharField(max_length=200, default=None,
                                   null=True, blank=True,)
    filename_original = models.CharField(max_length=200, default=None,
                                         null=True, blank=True,)
    file_field = models.FileField(default=None, null=True, blank=True,
                                  upload_to=generate_filename, )

    def url(self, default=None):
        f = self.file_field
        if f is None:
            if default:
                return static(default)
            return static('img/no-image-yet.jpg')
        return reverse_lazy('url_public',
                            args=(f.name[2:]
                                  if f.name.startswith('./') else f.name,))

    def os_full_filename(self):
        name = os.path.join(settings.MEDIA_ROOT, str(self.file_field))
        return name if os.path.isfile(name) else None

    def file_description(self):
        mime = magic.Magic(mime=True)
        name = self.os_full_filename()
        if name is None:
            return None
        result = mime.from_file(name)
        tab = result.split('/')
        if len(tab) == 2:
            if tab[0] == 'image':
                return 'image'
            if tab[1] == 'pdf':
                return 'pdf'
        return result

    def __str__(self):
        return str(self.file_field)

    class Meta:
        abstract = True


class Picture(BaseFileModel):

    @cached_property
    def url_thumbnail(self, default='-'):
        f = self.url(default)
        if f == '-':  # No image -> return whole image
            return self.url(None)
        f = f.split('/')
        i = len(f)-1
        while (i >= 0) and (f[i] != 'full'):  # 'full' codé en dur
            i -= 1
        if i < 0:  # Ne devrait jamais arriver
            return self.url(None)
        f[i] = 'th'
        return '/'.join(f)

    def __str__(self):
        return str(self.file_field)

