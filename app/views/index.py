from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.views import generic


class IndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'new/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Home")
        return context


class NewIndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'new/example.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Home")
        return context


class NewButtonsView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'new/buttons.html'


class NewCardsView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'new/cards.html'


class NewUtilitiesColorView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'new/utilities-color.html'


class NewUtilitiesBorderView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'new/utilities-border.html'


class NewUtilitiesAnimationView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'new/utilities-animation.html'


class NewUtilitiesOtherView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'new/utilities-other.html'


class New404View(generic.TemplateView):
    template_name = 'new/404.html'


class NewBlankView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'new/blank.html'


class NewChartsView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'new/charts.html'


class NewTablesView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'new/tables.html'


class OldIndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'index.html'
