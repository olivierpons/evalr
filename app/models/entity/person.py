import uuid
from datetime import datetime
from io import BytesIO

import requests
from PIL import Image
from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import get_current_timezone
from django.utils.translation import ugettext_lazy as _
from libgravatar import Gravatar

from app.forms.generic.generic import UploadedPictureHandler, DateUtilsMixin
from app.models.bulle import GroupeBulles
from core.models.base import BaseModel
from core.models.entity import Entity
from core.models.file.image import ImageFile
from core.models.profession import Profession


class GravatarFile(ImageFile):
    upload_directory = 'gravatar'

    def __str__(self):
        return '{}'.format(
            self.str_clean(self.original_filename, if_none=_("No file")))


class PersonManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_physical=True)


class Person(Entity):
    objects = PersonManager()
    user = models.OneToOneField(User, related_name='person',
                                on_delete=models.CASCADE)

    groupe_bulles = models.ForeignKey(GroupeBulles, blank=True,
                                      default=None, null=True,
                                      on_delete=models.CASCADE)
    gravatar = models.OneToOneField(GravatarFile, null=True, blank=True,
                                    default=None, on_delete=models.SET_NULL)

    confirmation_code = models.CharField(max_length=200, default=None,
                                         null=True, blank=True)
    reset_code = models.CharField(max_length=200, default=None,
                                  null=True, blank=True)

    # region - gravatar and person information (utils) -
    def gravatar_cached_image(self):

        def refresh_gravatar():
            gravatar_url = Gravatar(self.user.email).get_image()
            if 'http://' in gravatar_url:
                gravatar_url = 'https://{}'.format(gravatar_url[7:])
            response = requests.get(gravatar_url)
            img = Image.open(BytesIO(response.content))
            # filename example: 'www.gravatar.com-avatar-f976af5e922e17a4.png'
            filename = '{}.{}'.format(gravatar_url[8:].replace('/', '-'),
                                      img.format.lower())
            try:
                final = UploadedPictureHandler().generate_everything(
                    BytesIO(response.content), 'gravatar/',
                    thumbnail_dimensions=(60, 60),
                    uploaded_filename=filename)
                with transaction.atomic():
                    self.gravatar = GravatarFile.objects.create(
                        description='gravatar',
                        filename_original=gravatar_url,
                        file_field=final)
                    self.save()
            except IOError:
                pass

        try:
            if self.gravatar is None:
                refresh_gravatar()
            else:
                diff = DateUtilsMixin.make_datetime_aware(
                    datetime.now(),
                    timezone=get_current_timezone())
                if (diff - self.gravatar.date_last_modif).total_seconds() > 999:
                    refresh_gravatar()

            return self.gravatar.url_thumbnail
        except Exception as e:
            return str(e)

    def get_infos_name(self, tab):
        # try to get what's wanted otherwise still return something:
        def g(x):
            return x if x else ''

        retour = ' '.join([g(a) for a in tab]).strip()
        if not retour:
            retour = g(self.user.username)
            p = retour.find('_at_')
            retour = retour[:p - 1 if p > 0 else None]
        if not retour:
            retour = g(self.user.email).strip()
            p = retour.find('@')
            retour = retour[:p - 1 if p > 0 else None]
        return retour

    def get_first_name(self):
        return self.get_infos_name([self.user.first_name])

    def get_last_name(self):
        return self.get_infos_name([self.user.last_name])

    def full_name(self):
        return self.get_infos_name([self.user.first_name, self.user.last_name])
    # endregion - gravatar and person information (utils) -

    @staticmethod
    def create_username(email, unique=True):
        base_username = ''.join(
            [a for a in email.strip().replace('@', '_at_').lower()
             if a.isalnum() or a in ['_']])
        if not unique:
            return base_username
        # username has to be unique
        i = 0
        while True:
            username = '{}{}'.format(base_username,
                                     '_{}'.format(i) if i > 0 else '')
            try:
                User.objects.get(username=username)
                i += 1
            except User.DoesNotExist:
                break
        return username

    def __str__(self):
        def g(value, add_after=None):
            if not add_after:
                return value if value else ''
            return '{}{}'.format(value if value else '',
                                 add_after if value.strip() else '')

        u = self.user
        if u is None:
            return str(_("(no user)"))
        n = ' '.join([g(u.first_name), g(u.last_name)]).strip()
        n = '{}{}{}'.format(u.username, ' / ' if n else '', n).strip()
        return '{}{} - n.{}'.format(g(n, ' - '),
                                    u.email if u.email else _('(no email)'),
                                    str(self.pk))

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')
        ordering = ['user__last_name', 'user__first_name', 'pk']


class PersonProfession(BaseModel):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.person.simple_desc()} - ({str(self.profession)})'


class PersonConfirmation(BaseModel):
    person = models.ForeignKey(Person, on_delete=models.CASCADE,
                               related_name='person_confirmation')
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    used = models.BooleanField(default=False)


@receiver(post_save, sender=User)
def my_post_save_user_handler(sender, instance, created, **kwargs):
    if created:  # a User = physical -> create the associated person:
        Person.objects.create(user=instance, is_physical=True)