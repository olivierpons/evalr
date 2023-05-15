from django.conf.urls.i18n import i18n_patterns
from django.http import HttpResponseRedirect
from django.urls import re_path, path, include
from django.utils.translation import gettext_lazy as _
from django.views import static
from django.views.i18n import JavaScriptCatalog

from app.admin.admin import my_admin_site
from app.views.auth.forgot_password import ForgotPasswordView
from app.views.auth.login import AuthLoginView
from app.views.auth.logout import AuthLogoutView
from app.views.auth.password_reset import PasswordResetView
from app.views.auth.register import RegisterView
from app.views.auth.register_validate import RegisterValidateView
from app.views.wizard.index import WizardIndexView
from app.views.wizard.new_exam import WizardNewExamView
from app.views.wizard.new_learners_group import WizardNewLearnersGroupView
from app.views.wizard.new_exam_template import WizardNewExamTemplateView
from app.views.wizards import WizardsIndexView
from evalr import settings
from app.views.index import IndexView, NewIndexView, NewButtonsView, \
    NewCardsView, NewUtilitiesColorView, NewUtilitiesBorderView, \
    NewUtilitiesAnimationView, NewUtilitiesOtherView, New404View, \
    NewBlankView, NewChartsView, NewTablesView, OldIndexView
from app.views.interrogation_detail import InterrogationDetailView
from app.views.interrogation_list import InterrogationListView
from app.views.session_list import SessionListView
from app.views.personne_session import PersonneSessionDetailView
from app.views.icones_view import IconesView
from wizard.views.json.cancel import WizardJsonCancelView
from wizard.views.json.goto import WizardJsonGotoView
from wizard.views.json.help import WizardJsonHelpView
from wizard.views.json.reset import WizardJsonResetView
from wizard.views.json.step.view import WizardJsonStepView

urlpatterns = [
    path('^i18n/', include('django.conf.urls.i18n')),
    path('admin/', my_admin_site.urls),
    # pour ma surcharge complète de l'admin :
    # path('^hqf-admin/', my_admin_site.urls),
    path('^oauth/', include('social_django.urls', namespace='social')),

    path('^public/(?P<path>.*)$', static.serve, {
        'document_root': settings.MEDIA_ROOT
    }, name='url_public'),

    re_path('^icons/?$', IconesView.as_view(), name='view_icons'),
    re_path('^favicon.ico/$',  # google chrome favicon fix :
            lambda x: HttpResponseRedirect(settings.STATIC_URL+'favicon.ico')),
]
urlpatterns += i18n_patterns(
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    # region - auth URLs -
    path('login/', AuthLoginView.as_view(), name='auth_login'),
    path('logout/', AuthLogoutView.as_view(), name='auth_logout'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    re_path('^register-validate/(?P<rand_str>[a-zA-Z0-9-_]+)/$',
            RegisterValidateView.as_view(), name='auth_register_validate'),
    path('forgot-password/',
         ForgotPasswordView.as_view(), name='auth_forgot_password'),
    re_path('password-reset/(?P<rand_str>[a-zA-Z0-9-_]+)/$',
            PasswordResetView.as_view(), name='auth_password_reset'),
    # endregion - auth URLs -

    # region - Django (not used: officially not finished) register / login -
    # Django has not finished the whole register / login process
    # that's why I've stopped trying to use it, and I've implemented my own:
    # path('accounts/', include('django.contrib.auth.urls')),
    # path('accounts/password_change/', name='password_change'),
    # path('accounts/password_change/done/', name='password_change_done'),
    # path('accounts/password_reset/', name='password_reset'),
    # path('accounts/password_reset/done/', name='password_reset_done'),
    # path('accounts/reset/<uidb64>/<token>/', name='password_reset_confirm'),
    # path('accounts/reset/done/', name='password_reset_complete'),
    # endregion

    path('new',                  NewIndexView.as_view(),              name='app_new_index'),
    path('n/buttons',             NewButtonsView.as_view(),            name='app_new_buttons'),
    path('n/cards',               NewCardsView.as_view(),              name='app_new_cards'),
    path('n/utilities/color',     NewUtilitiesColorView.as_view(),     name='app_new_utilities_color'),
    path('n/utilities/border',    NewUtilitiesBorderView.as_view(),    name='app_new_utilities_border'),
    path('n/utilities/animation', NewUtilitiesAnimationView.as_view(), name='app_new_utilities_animation'),
    path('n/utilities/other',     NewUtilitiesOtherView.as_view(),     name='app_new_utilities_other'),
    path('n/404',                  New404View.as_view(),                name='app_new_404'),
    path('n/blank',                NewBlankView.as_view(),              name='app_new_blank'),
    path('n/charts',               NewChartsView.as_view(),             name='app_new_charts'),
    path('n/tables',               NewTablesView.as_view(),             name='app_new_tables'),

    path('', IndexView.as_view(), name='app_index'),
    path(_('^wizards/?$'), WizardsIndexView.as_view(), name='app_wizards'),
    path(_('^wizard/?$'), WizardIndexView.as_view(), name='app_wizard_main'),
    path(_('^wizard/new-examination-template/?$'),
         WizardNewExamTemplateView.as_view(), name='wz_new_exam_template'),
    path(_('^wizard/new-exam/?$'),
         WizardNewExamView.as_view(), name='wz_new_exam'),
    path(_('^wizard/new-learners-group/?$'),
         WizardNewLearnersGroupView.as_view(), name='wz_new_learners_group'),

    path('^old$', OldIndexView.as_view(), name='app_old_index'),
    path(_('^interrogation/(?P<slug>[^/.]+)/$'),
         InterrogationDetailView.as_view(), name='app_interrogation'),
    path(_('^interrogations/$'),
         InterrogationListView.as_view(), name='app_interrogations'),
    path(_('^sessions/$'),
         SessionListView.as_view(), name='app_sessions'),
    path(_('^session/(?P<pk>[0-9]+)/$'),
         PersonneSessionDetailView.as_view(), name='app_person_session'),

    # region - wizard views -
    path('json/wz/step/<slug:uuid>/<slug:company>',
         WizardJsonStepView.as_view(), name='wizard_json_step'),
    path('json/wz/reset/<slug:uuid>/<slug:company>',
         WizardJsonResetView.as_view(), name='wizard_json_reset'),
    path('json/wz/cancel/<slug:uuid>/<slug:company>',
         WizardJsonCancelView.as_view(), name='wizard_json_cancel'),
    path('json/wz/goto/<slug:uuid>/<slug:company>',
         WizardJsonGotoView.as_view(), name='wizard_json_goto'),
    path('json/wz/help/<slug:company>',
         WizardJsonHelpView.as_view(), name='wizard_json_help'),
    # endregion - wizard views -
)
