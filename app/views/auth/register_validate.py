from django.contrib.auth import login
from django.contrib.auth.views import logout_then_login
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic
from django.utils.translation import gettext_lazy as _

from app.models.entity.person import Person
from app.utils import add_messages
from evalr import settings


class RegisterValidateView(generic.View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        try:
            rand_str = kwargs.get('rand_str', '-')
            p = Person.objects.get(confirmation_code=rand_str)

            if request.user.is_authenticated:
                if p.user != self.request.user:
                    # already logged, but not the same user
                    add_messages(self.request,
                                 _("Already logged in"),
                                 [_("You were logged as another user"),
                                  _("You have been disconnected"),
                                  _("Please reconnect")])
                return logout_then_login(request)

            # came here = People found
            # - if already activated, login + redirect to index
            #
            if p.user.is_active:
                # not logged in, , but already activated:
                login(request, p.user,
                      # manually precise backend otherwise conflicts:
                      backend='django.contrib.auth.backends.ModelBackend')
                add_messages(self.request,
                             _("Account activated!"),
                             [_("You have been automatically logged"),
                              _("(your account was already activated)"), ])
            else:
                # not logged in, People found and not activated:
                login(request, p.user,
                      # manually precise backend otherwise conflicts:
                      backend='django.contrib.auth.backends.ModelBackend')
                p.user.is_active = True
                p.user.save()
                add_messages(self.request,
                             _("Account activated!"),
                             [_("Welcome to {}!").format(settings.WEBSITE_NAME),
                              _("Congratulations!"),
                              _("Your account has been activated!"), ])
        except Person.DoesNotExist:  # hack -> no message, nothing:
            return HttpResponseRedirect(reverse_lazy('auth_login'))

        return HttpResponseRedirect(reverse_lazy('app_new_index'))
