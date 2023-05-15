from collections import OrderedDict

from django import forms
from django.forms import widgets
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        # from /../site-packages/django/contrib/auth/forms.py
        e = {'required': _("This field is required"),
             'invalid_login': _("Please enter a correct %(username)s "
                                "and password. "
                                "Note that both fields may be case-sensitive."),
             'inactive': _("This account is inactive."), }

        username_or_email = forms.CharField(label=_("Email"),
                                            localize=True, required=True,
                                            widget=widgets.TextInput(
                                                attrs={'autofocus': True, }),
                                            error_messages=e,)

        password = forms.CharField(label=_("Password"),
                                   localize=True, required=True,
                                   strip=False,
                                   widget=forms.PasswordInput,)
        self.fields = OrderedDict([
            ('username_or_email', username_or_email),
            ('password', password),
        ])

    # from /../site-packages/django/contrib/auth/forms.py
    def get_invalid_login_error(self):
        return forms.ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
            params={'username': self.username_field.verbose_name},
        )
