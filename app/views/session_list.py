import pytz
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import translation
from django.utils.datetime_safe import datetime
from django.utils.translation import gettext_lazy as _
from django.views import generic

from app.models.entity.person import Person
from app.models.interrogation import Interrogation
from app.models.personne_session import PersonneSession
from evalr import settings


class SessionListView(LoginRequiredMixin, generic.ListView):
    model = PersonneSession
    template_name = 'personnesession_list.html'

    def __init__(self, **kwargs):
        self.locale = translation.get_language().split('-')[0]
        super(SessionListView, self).__init__(**kwargs)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return None
        local_dt = datetime.now(tz=pytz.timezone(settings.TIME_ZONE))
        p = Person.objects.filter(user=self.request.user)
        interrogations = Interrogation.objects.filter(persons__in=p)
        sessions = PersonneSession.objects.filter(
            Q(interrogation__in=interrogations) &
            Q(date_v_start__lte=local_dt) &
            # date with no expiration date or not expired:
            (Q(date_v_end__isnull=True) | Q(date_v_end__gt=local_dt))
        )
        return sessions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object_list is not None:
            context['sessions'] = [
                {'description': _(' - ').join([str(i.interrogation),
                                               str(i.modele)]),
                 'pk': str(i.pk),
                 } for i in self.object_list]
        return context
