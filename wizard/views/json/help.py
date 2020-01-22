from django.http import JsonResponse
from django.views.generic.base import View


class WizardJsonHelpView(View):
    def get(self, request, **kwargs):
        return JsonResponse({'tou': 'dlkjf'})
