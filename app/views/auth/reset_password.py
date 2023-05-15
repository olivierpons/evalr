from django.contrib.auth.forms import PasswordChangeForm
from django.views import generic
from django.utils.translation import gettext_lazy as _

from app.utils import add_messages


class MyResetPasswordView(generic.FormView):
    form_class = PasswordChangeForm
    template_name = 'auth/forgot-password.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Password reset")
        return context

    def form_valid(self, form):
        add_messages(self.request,
                     _("Password reset!"),
                     [_("Your password has been successfully reset."),
                      _("You can now login with your new password.")])
        return super().form_valid(form)
