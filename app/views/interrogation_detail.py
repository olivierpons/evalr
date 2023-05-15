from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.views import generic

from app.models.interrogation import Interrogation


class InterrogationDetailView(generic.DetailView):
    model = Interrogation
    slug_field = 'description'

    def __init__(self, **kwargs):
        self.locale = translation.get_language().split('-')[0]
        super(InterrogationDetailView, self).__init__(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object is None:
            return context

        context[u'interrogation'] = {
            u'description': _(self.object.description),
        }

        return context
