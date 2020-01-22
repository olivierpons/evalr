from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy


class AuthLogoutView(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy('app_new_index')
