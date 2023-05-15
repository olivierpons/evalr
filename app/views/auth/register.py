import uuid

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from django.views import generic
from django.utils.translation import gettext_lazy as _

from app.forms.register import RegisterForm
from app.models.entity.person import Person
from evalr import settings


class RegisterView(generic.FormView):
    form_class = RegisterForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('auth_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Registration")
        return context

    def form_valid(self, form):
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('email')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password_1')
        try:
            User.objects.get(email=email)
            form.add_error('email', _("Email already used"))
            return super().form_invalid(form)
        except User.DoesNotExist:
            pass

        # ! When create_user is called, a new Person is created
        #   via my_post_save_user_handler():
        user = User.objects.create_user(username=Person.create_username(email),
                                        email=email,
                                        first_name=first_name,
                                        last_name=last_name,
                                        password=password,
                                        is_active=False)
        # ! Person created through signal -> just read it:
        p = user.person
        p.confirmation_code = str(uuid.uuid4())  # generate random str
        p.save()

        # region - send_mail -
        # used a lot copy/paste. there's room for improvement here:
        site_web = '{}://{}'.format(self.request.scheme,
                                    self.request.META['HTTP_HOST'])
        email_message = EmailMessage(
            subject=_("Thanks for registering!"),
            body='{}\n{}\n{}\n{}{}'.format(
                _("Thanks for signing up!"),
                _("We sincerely hope that you will appreciate this "
                  "new and innovative international way to "
                  "teach / and / or / learn things, "
                  "for which the operative word is “fun”"),
                _("To validate your registration, "
                  "click on the following link:"),
                site_web,
                reverse_lazy('auth_register_validate',
                             kwargs={'rand_str': p.confirmation_code})
            ),
            from_email=f'contact@{settings.WEBSITE_NAME}.com',
            reply_to=[f'contact@{settings.WEBSITE_NAME}.com'],
            to=[form.cleaned_data['email']],
            bcc=['olivier.pons@gmail.com'],)
        # email_message.attach('design.png', img_data, 'image/png')
        email_message.send()
        # endregion

        messages.add_message(self.request, messages.SUCCESS,
                             _("Successful registration!"))
        messages.add_message(self.request, messages.SUCCESS,
                             _("An email containing an activation link has "
                               "been sent to the email address you provided."))
        return super(RegisterView, self).form_valid(form)
