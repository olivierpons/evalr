import uuid

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic
from django.utils.translation import ugettext_lazy as _

from app.utils import add_messages
from evalr import settings


class ForgotPasswordView(generic.FormView):
    template_name = 'auth/forgot-password.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('auth_forgot_password')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Forgot your password?")
        return context

    def form_valid(self, form):
        user = None
        email = form.cleaned_data.get('email')
        if email:
            try:
                # Check the form.send_mail()! I should use it, but it's longer
                # than copy/paste my (working code) to send a mail:
                user = User.objects.get(email__iexact=email, is_active=True)
                if not user.has_usable_password():
                    user = None
            except User.DoesNotExist:
                pass

        if user is not None:
            p = user.person
            if p is None:
                add_messages(self.request,
                             _("You're a social person!"),
                             [_("You registered here via a social network."),
                              _("Please connect via a social network "
                                "available here.")])
                return HttpResponseRedirect(reverse_lazy('auth_login'))

            # Person exists:
            p.reset_code = str(uuid.uuid4())  # generate random str
            p.save()
            # he registered via classical registration:
            # region - send_mail -
            # used a lot copy/paste. there's room for improvement here:
            site_name = self.request.META['HTTP_HOST']
            site_web = '{}://{}'.format(self.request.scheme, site_name)
            email_message = EmailMessage(
                subject=_("Password reset"),
                body='{}\n{}\n{}\n\n{}\n{}\n\n{}'.format(
                    _("You've asked to reset your password on %(site_name)s") %
                    {'site_name': site_name.split(':')[0]},
                    _("Please go to the following page "
                      "and choose a new password:"),
                    "{}{}".format(
                        site_web,
                        reverse_lazy('auth_password_reset',
                                     kwargs={'rand_str': p.reset_code})
                    ),
                    _("Thanks for using our site!"),
                    _("See you soon on %(site_name)s") %
                    {'site_name': site_name.split(':')[0]},
                    _("The %(site_name)s's team") %
                    {'site_name': site_name.split(':')[0]},
                ),
                from_email=f'contact@{settings.WEBSITE_NAME}.com',
                reply_to=[f'contact@{settings.WEBSITE_NAME}.com'],
                to=[form.cleaned_data['email']],
                bcc=['olivier.pons@gmail.com'], )
            # email_message.attach('design.png', img_data, 'image/png')
            email_message.send()
            # endregion

        add_messages(self.request,
                     _("Email sent!"),
                     [_("A reset link has been sent"),
                      _("(if your email is in our database).")])
        return super(ForgotPasswordView, self).form_valid(form)
