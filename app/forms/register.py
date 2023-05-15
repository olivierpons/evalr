from collections import OrderedDict

from django import forms
from django.forms import widgets
from django.utils.translation import gettext_lazy as _


class RegisterForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        # from /../site-packages/django/contrib/auth/forms.py
        e = {'required': _("This field is required"),
             'invalid': _("This field contains invalid data")}

        first_name = forms.CharField(label=_("Email"),
                                     localize=True, required=True,
                                     widget=widgets.TextInput(
                                         attrs={'autofocus': True, }),
                                     error_messages=e,)
        last_name = forms.CharField(label=_("Email"),
                                    localize=True, required=True,
                                    widget=widgets.TextInput,
                                    error_messages=e,)
        email = forms.CharField(label=_("Email"),
                                localize=True, required=True,
                                widget=widgets.TextInput,
                                error_messages=e,)
        password_1 = forms.CharField(label=_("Password"),
                                     localize=True, required=True,
                                     widget=widgets.PasswordInput,
                                     error_messages=e,)
        password_2 = forms.CharField(label=_("Repeat password"),
                                     localize=True, required=True,
                                     widget=widgets.PasswordInput,
                                     error_messages=e,)

        self.fields = OrderedDict([('first_name', first_name),
                                   ('last_name', last_name),
                                   ('email', email),
                                   ('password_1', password_1),
                                   ('password_2', password_2),
                                   ])

    def clean(self):
        password_1 = self.cleaned_data.get('password_1', '')
        password_2 = self.cleaned_data.get('password_2', '')
        if password_1 != password_2:
            self.add_error('password_1', _("Passwords do not match"))
            self.add_error('password_2', _("Passwords do not match"))
            return None
        return super(RegisterForm, self).clean()

