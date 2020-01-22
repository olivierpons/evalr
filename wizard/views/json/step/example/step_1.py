from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from wizard.views.json.base import WizardBase


class WizardStepExampleStep1(WizardBase):
    description = _("Step 1")
    breadcrumb = _("Step 1")

    def get_content(self, request, wz_user_step, data, **kwargs):
        """
        Args:
            request: the current request
            wz_user_step: current wz_user_step model
            data: all data gathered step after step
            **kwargs: other arguments (company and uuid amongst others)

        Returns:
            Object that should be returned as JSON
        """
        return [
            {'type': 'text',
             'line_break': False,
             'data': [
                 {'type': 'title_2',
                  'content': _("Step 1")},
                 {'type': 'title_4',
                  'content': _("Phrase")},
                 {'type': 'p',
                  # 'class': 'important warning',
                  'content': _("Une phrase est composée de plusieurs "
                               "'parties' : (a) +  (b) +  (c) +  (d) ...")},
                 {'type': 'p',
                  'line_break': True,  # line break *inside*, only here:
                  'content': [
                      _("Chaque morceau est une expression simple "
                        "ex: 'Complément circonstanciel de temps'. "),
                      _("Seulement, comme plein de ces expressions "
                        "sont réutilisées, je les ai découpées en "
                        "'groupe de catégories' qui contiennent une ou "
                        "plusieurs catégories "
                        "(et c'est ça qui est dur à comprendre pour moi)")]},
                 {'type': 'title_4',
                  'content': _("Expression")},
                 {'type': 'p',
                  'line_break': True,  # line break *inside*, only here:
                  'content': [
                      _("Une expression = un mot ou même une phrase en entier "
                        "(ex: le verbe conjugué en entier : 'je désole')"),
                      _("Une expression appartient à un ou plusieurs "
                        "groupes de catégories"),
                  ]},
                 {'type': 'title_4',
                  'content': _("Groupes d'expressions")},
                 {'type': 'p',
                  'line_break': True,  # line break *inside*, only here:
                  'content': [
                      _("Quand on commence à avoir trop d'expressions, il "
                        "faudrait les grouper, sinon, pour faire une "
                        "interrogation, c'est une galère pas possible"),
                      _("=> j'ai défini des \"groupes d'expressions\""),
                  ]},
                 {'type': 'title_4',
                  'content': _("Comment faire une interrogation ?")},
                 {'type': 'p',
                  'line_break': True,  # line break *inside*, only here:
                  'content': [
                      _("1) Aller dans les modèles d'interrogation"),
                      _("2) Choisir les expressions qui sont à sortir pour "
                        "l'interrogation. pour me simplifier la vie, "
                        "j'ai fait des \"groupes d'expressions\"."),
                      _("Donc au lieu de choisir des expressions, il faut "
                        "choisir des \"groupes d'expressions\". "
                        "Ça paraît plus énervant au début, "
                        "mais dès qu'on a beaucoup d'expressions, ça devient "
                        "super pratique"),
                      _("3) il faut choisir les modèles de phrases qui "
                        "serviront de base (= pour construire les "
                        "phrases 'finales' proposées aux apprenants)."),
                      _("Il faut choisir les expressions et les phrases, "
                        "de manière à ce que, lors de la construction, "
                        "on puisse 'remplir' complètement les phrases "
                        "avec les expressions"),
                      _("4) aller dans interrogations, "
                        "et en créer une nouvelle : "
                        "choisir le modèle qu'on vient juste de créer, "
                        "et y ajouter des participants"),
                      _("5) aller dans interrogation > sessions et "
                        "créer une nouvelle session par "
                        "participant à l'interrogation"),
                  ]},
                 {'type': 'p',
                  'content': [
                      _("This is where you can generate a new session."),
                      _("Note: \"session\" is not an \"interrogation\" !"),
                      _("If you are new to what a session is, "
                        "checkout <a href=\"{}\">this link</a>.").format(
                          reverse_lazy('app_wizard_main'))
                  ]}
             ]},
            {'type': 'buttons',
             'data': {
                 'prev': '',
                 'next': 'step_2'
             }}
        ]

    def set_prev_step(self, new_step, request, data, **kwargs):
        """
        Analyze parameters and if it's ok returns the previous step
        (*without modifying database*)

        Args:
            new_step: new_step (coming from user choice)
            request: the current request
            data: all data gathered step after step
            **kwargs: other arguments (company and uuid amongst others)

        Returns:
            5 values:
                - success: True or False if success,
                - new_user_step: New step (ignored if success == False)
                - breadcrumb_detail: (ignored here (= previous step))
                - db_data: None = ignored else data to write *for current step*
                - result: (ignored here -> return only {'success': True, } )
        """
        # should never call back here: it's the first step!
        return self.incorrect_step_result()

    def set_next_step(self, new_step, request, data, **kwargs):
        """
        Analyze parameters and if it's ok returns the next step
        (*without modifying database*)

        Args:
            new_step: new_step (coming from user choice)
            request: the current request
            data: all data gathered step after step
            **kwargs: other arguments (company and uuid amongst others)

        Returns:
            5 values:
                - success: True or False if success,
                - new_user_step: New step (ignored if success == False)
                - breadcrumb_detail: Detail to show (summary of choices done)
                - db_data: Data to remember into database (if any)
                - result: Object to JSON-encode for the AJAX result
        """
        if new_step not in ['step_2']:
            return self.incorrect_step_result()

        # data to save in database:
        db_data = None

        # local import to avoid circular reference
        from wizard.models.wz_user_step import WzUserStep
        return True, WzUserStep.WZ_STEP_EXAMPLE_STEP_2, \
            str(_("Explanation done")), db_data, {'success': True, }
