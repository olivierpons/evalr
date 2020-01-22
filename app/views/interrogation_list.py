from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from app.models.interrogation import Interrogation


class InterrogationListView(generic.ListView):
    model = Interrogation

    def __init__(self, **kwargs):
        self.locale = translation.get_language().split('-')[0]
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object_list is not None:
            context['interrogations'] = [
                {'description': _(' - ').join([i.description]), }
                for i in self.object_list]
        return context
