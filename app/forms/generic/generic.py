import os
import uuid

from os.path import splitext, basename, abspath, join

import PIL
from PIL import ExifTags
from PIL import Image
from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils import formats
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.timezone import make_aware, utc, localtime
from django.utils.datetime_safe import datetime as datetime_safe
from django.utils.translation import ugettext_lazy as _
from datetime import time, date as datetime_date
from datetime import datetime as datetime_classic

from numpy import random

from evalr.settings import MEDIA_ROOT


class UidMixin(object):
    @staticmethod
    def generate_uid(text_to_append='', salt=''):
        # pris ici : http://stackoverflow.com/questions/
        # 6999726/how-can-i-convert-a-datetime-object-to
        # -milliseconds-since-epoch-unix-time-in-p
        epoch = datetime_safe.utcfromtimestamp(0)

        def millis(dt):
            return (dt - epoch).total_seconds() * 1000.0

        nom = str(random.randint(0, 90000000) +
                  int(millis(datetime_safe.now())))
        return str(uuid.uuid5(uuid.NAMESPACE_OID, nom + salt)) + text_to_append


class DateUtilsMixin(object):

    @staticmethod
    def make_date_aware(d=None, timezone=utc):
        # rendre la date entrée "aware" en utc
        if d is None:
            return make_aware(datetime_safe.now(),
                              timezone=timezone)
        elif type(d) is str:
            return make_aware(datetime_safe.combine(parse_date(d),
                                                    time(0, 0, 0)),
                              timezone=timezone)
        elif type(d) is datetime_date or type(d) is datetime_classic:
            return make_aware(datetime_safe.combine(d, time(0, 0, 0)),
                              timezone=timezone)
        return d

    @staticmethod
    def make_datetime_aware(d=None, timezone=utc):
        # rendre la date entrée "aware" en utc
        if d is None:
            return make_aware(datetime_safe.now(),
                              timezone=timezone)
        elif type(d) is str:
            return make_aware(parse_datetime(d), timezone=timezone)
        elif type(d) is datetime_date or type(d) is datetime_classic:
            return make_aware(d, timezone=timezone)
        return d

    @staticmethod
    def make_date_local(d):
        return localtime(d)


class UploadedFileHandler(object):
    @staticmethod
    def get_url(name, path=None):
        retour = (path if path else '') + name
        # Ex: "profiles/bea536a0/089c/a45b.jpg"
        return retour.replace('-', '/')

    @staticmethod
    def full_filename(filename):
        return abspath(join(MEDIA_ROOT, filename))

    @staticmethod
    def make_dir(dst):
        dst_base = os.path.dirname(dst)
        if not os.path.exists(dst_base):
            os.makedirs(dst_base, 0o777)

    @staticmethod
    def generate_filename(extension):
        return UidMixin.generate_uid(extension)

    @staticmethod
    def save(uploaded_file, dst):
        # https://docs.djangoproject.com/en/dev/
        # topics/http/file-uploads/#writing-custom-upload-handlers
        # selon la documentation : il faut sauver à la main, copier coller
        # de leur exemple :
        with open(dst, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)


class UploadedPictureHandler(UploadedFileHandler):

    @staticmethod
    def compute_url_fullsize(name, path=None):
        # -> dst : "profiles/full/bea536a0-089c-a45b.jpg"
        return UploadedPictureHandler.get_url(name,
                                              (path if path else '') + 'full/')

    @staticmethod
    def compute_url_thumbnail(name, path=None):
        # -> dst : "profiles/th/bea536a0-089c-a45b.jpg"
        return UploadedPictureHandler.get_url(name,
                                              (path if path else '') + 'th/')

    @staticmethod
    def compute_urls(nom, path_dest):
        return (UploadedPictureHandler.compute_url_fullsize(nom, path_dest),
                UploadedPictureHandler.compute_url_thumbnail(nom, path_dest))

    @staticmethod
    def full_filenames(filename, filename_thumbnail):
        return (UploadedFileHandler.full_filename(filename),
                UploadedFileHandler.full_filename(filename_thumbnail))

    @staticmethod
    def make_dirs(dst_full, dst_full_thumbnail):
        UploadedFileHandler.make_dir(dst_full)
        UploadedFileHandler.make_dir(dst_full_thumbnail)

    @staticmethod
    def save_image(img, dst, dst_thumbnail, thumbnail_dimensions=(),
                   return_thumbnail=False):
        # Ex: "C:\Users\...\uploads\profiles\full\bea536a0\089c\a45b.jpg"
        #     "C:\Users\...\uploads\profiles\th\bea536a0\089c\a45b.jpg"
        dst_full, dst_full_thumbnail = \
            UploadedPictureHandler.full_filenames(dst, dst_thumbnail)

        UploadedPictureHandler.make_dirs(dst_full, dst_full_thumbnail)

        img.save(dst_full)
        if len(thumbnail_dimensions) == 2:
            w_thumbnail, h_thumbnail = thumbnail_dimensions
            percent = min(w_thumbnail / float(img.size[0]),
                          h_thumbnail / float(img.size[1]))
            img = img.resize((int(float(img.size[0])*percent),
                              int(float(img.size[1])*percent)),
                             PIL.Image.ANTIALIAS)
            img.save(dst_full_thumbnail)
            if return_thumbnail:
                return dst_thumbnail  # relative filename

        return dst  # relative filename

    @staticmethod
    def generate_everything(uploaded_file, path_dest=None,
                            thumbnail_dimensions=(),
                            return_thumbnail=False,
                            uploaded_filename=None):

        img = Image.open(uploaded_file)
        try:
            # rotation img code
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    try:
                        exif = dict(img._getexif().items())
                        if exif[orientation] is 6:
                            img = img.rotate(-90, expand=True)
                        elif exif[orientation] is 8:
                            img = img.rotate(90, expand=True)
                        elif exif[orientation] is 3:
                            img = img.rotate(180, expand=True)
                        elif exif[orientation] is 2:
                            img = img.transpose(
                                Image.FLIP_LEFT_RIGHT, expand=True)
                        elif exif[orientation] is 5:
                            img = img.rotate(-90).transpose(
                                Image.FLIP_LEFT_RIGHT, expand=True)
                        elif exif[orientation] is 7:
                            img = img.rotate(90, expand=True).transpose(
                                Image.FLIP_LEFT_RIGHT, expand=True)
                        elif exif[orientation] is 4:
                            img = img.rotate(180).transpose(
                                Image.FLIP_LEFT_RIGHT, expand=True)
                        break
                    except ZeroDivisionError:
                        # error unknown due to PIL/TiffImagePlugin.py buggy
                        # -> ignore this "rotation img" code, just continue
                        break
        except (AttributeError, KeyError, IndexError):
            # cases: image don't have getexif
            # -> ignore this "rotation img" code, just continue
            pass
        nom = uploaded_filename or UploadedFileHandler.generate_filename(
            splitext(basename(uploaded_file.name))[1])

        # Ex: "profiles/bea536a0-089c-a45b.jpg"
        # -> dst  : "profiles/full/bea536a0-089c-a45b.jpg"
        # -> thumb: "profiles/th/bea536a0-089c-a45b.jpg"
        dst, dst_thumbnail = UploadedPictureHandler.compute_urls(nom, path_dest)

        return UploadedPictureHandler.save_image(img, dst, dst_thumbnail,
                                                 thumbnail_dimensions,
                                                 return_thumbnail)


class BaseFormForceLocalizedDateFields(forms.BaseForm):

    def __init__(self, *args, **kwargs):
        super(BaseFormForceLocalizedDateFields, self).__init__(*args, **kwargs)
        # Le principe : la traduction de Django... en anglais est un problème !
        # Le format appliqué en fonction de la langue courante par défaut
        # est le premier du tableau formats.get_format('DATE_INPUT_FORMATS')
        # ...codé en dur dans la classe DateTimeBaseInput :
        # -> rechercher la fonction _format_value()
        # Bref. Par défaut, le format international anglais
        # renvoie "Y-m-d", au lieu de "m/d/Y". Soit j'ai loupé quelque chose,
        # soit c'est du n'importe quoi.
        # Mais en regardant de plus près le deuxième item du tableau
        # 'DATE_INPUT_FORMATS', je vois qu'il est pour toutes les langues
        # presque sur le même principe du genre "d/m/y" ou  "m/d/y".
        # Donc je hacke : dans le constructeur, les widgets sont déjà crées,
        # donc je force à la main les widgets de type DateInput qui sont
        # localisés ET qui n'ont pas de format spécifique assigné.
        # Hack à supprimer le jour le core de Django a corrigé cela :
        force = formats.get_format('DATE_INPUT_FORMATS')[1]
        for k, v in self.fields.items():
            if isinstance(v.widget, widgets.DateInput):
                # si date localisé SANS format, alors surcharger :
                if getattr(v, 'localize', False):
                    if not getattr(v.widget, 'format', None):
                        v.widget.format = force


# même que la classe au dessus, mais pour les Form :
class FormForceLocalizedDateFields(forms.Form,
                                   BaseFormForceLocalizedDateFields,):
    pass


# même que la classe au dessus, mais pour les ModelForm :
class ModelFormForceLocalizedDateFields(forms.ModelForm,
                                        BaseFormForceLocalizedDateFields,):
    pass


class BackFieldFormMixin(forms.BaseForm):
    """ 
    Classe qui crée un bouton 'Back' caché qui ressort dans le formulaire
    (!) À utiliser conjointement avec une vue descendante de XxxxWithBackView 
    """

    def __init__(self, *args, **kwargs):
        super(BackFieldFormMixin, self).__init__(*args, **kwargs)
        e = {'required': _("This field is required"),
             'invalid': _("This field contains invalid data")}
        back = forms.CharField(label='',
                               widget=forms.HiddenInput(),
                               error_messages=e)
        self.fields.update({'back': back})


class BaseWithBackFieldForm(FormForceLocalizedDateFields,
                            BackFieldFormMixin):
    pass


class ModelWithBackFieldForm(ModelFormForceLocalizedDateFields,
                             BackFieldFormMixin):
    pass


# validation used by societe / url field.
def validate_domain_name(value):
    if value != ''.join(e for e in value if e.isalnum() or e in '_-.'):
        raise ValidationError(_('Url must contains only alphanumerics,'
                                ' "_", "-" or "." characters'))
