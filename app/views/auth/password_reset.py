from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic
from django.utils.translation import ugettext_lazy as _

from app.models.entity.person import Person
from app.utils import add_messages


class PasswordResetView(generic.FormView):
    template_name = 'auth/password-reset.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('app_new_index')

    def __init__(self):
        super(PasswordResetView, self).__init__()
        self.form_user = None

    def init_form_user(self, **kwargs):
        try:
            self.form_user = Person.objects.get(
                reset_code=kwargs.get('rand_str')
            ).user
        except Person.DoesNotExist:
            pass

    # region - init form_user in get() or post()
    def get(self, request, *args, **kwargs):
        self.init_form_user(**kwargs)
        if self.form_user is None:
            return HttpResponseRedirect(reverse_lazy('app_login'))
        return super(PasswordResetView, self).get(reverse_lazy,
                                                  *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.init_form_user(**kwargs)
        if self.form_user is None:
            return HttpResponseRedirect(reverse_lazy('app_login'))
        return super(PasswordResetView, self).post(reverse_lazy,
                                                   *args, **kwargs)
    # endregion

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Change password")
        return context

    # Copy/paste of code at site-packages/django/contrib/auth/views.py
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # kwargs['user'] = self.request.user
        kwargs['user'] = self.form_user
        return kwargs

    def form_valid(self, form):
        # Copy/paste of code at site-packages/django/contrib/auth/views.py
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)

        add_messages(self.request,
                     _("Password reset!"),
                     [_("Your password has been reset!"),
                      _("You can login with your new password.")])
        return super(PasswordResetView, self).form_valid(form)
