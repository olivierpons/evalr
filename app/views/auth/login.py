from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect

from app.utils import add_messages


class AuthenticationWithEmailForm(AuthenticationForm):

    def clean(self):
        username_or_email = self.cleaned_data.get('username')
        try:
            User.objects.get(username=username_or_email)
            # if ok -> no exception -> do nothing
        except User.DoesNotExist:
            try:
                # try by email:
                u = User.objects.get(email=username_or_email)
                # if found, change the username:
                self.cleaned_data['username'] = u.username
            except User.DoesNotExist:
                pass
        return super(AuthenticationWithEmailForm, self).clean()


class AuthLoginView(LoginView):
    form_class = AuthenticationWithEmailForm
    template_name = 'auth/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            add_messages(self.request,
                         _("Already logged in"),
                         [_("You are already logged."),
                          _("If you want to logout:"),
                          _("- click on your username"),
                          _("- click on {logout}")])
            return HttpResponseRedirect(reverse_lazy('app_new_index'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Home")
        return context

    def form_valid(self, form):
        # # ! TODO: handle session automatic timeout
        # if self.request.POST.get('remember_me', None):
        #     self.request.session.set_expiry(0)
        # else:
        #     self.request.session.set_expiry(60 * 5)  # 5 minutes
        return super().form_valid(form)


