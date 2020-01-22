from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.http import HttpResponseRedirect
from django.urls import re_path, path
from django.utils.translation import ugettext_lazy as _
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
    url(r'^i18n/', include('django.conf.urls.i18n')),
    path('admin/', my_admin_site.urls),
    # pour ma surcharge complète de l'admin :
    # url(r'^hqf-admin/', my_admin_site.urls),
    url(r'^oauth/', include('social_django.urls', namespace='social')),

    url(r'^public/(?P<path>.*)$', static.serve, {
        'document_root': settings.MEDIA_ROOT
    }, name='url_public'),

    url(r'^icons/?$', IconesView.as_view(), name='view_icons'),
    url(r'^favicon.ico/$',  # google chrome favicon fix :
        lambda x: HttpResponseRedirect(settings.STATIC_URL+'favicon.ico')),
]
urlpatterns += i18n_patterns(
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    # region - auth URLs -
    url(r'login/', AuthLoginView.as_view(), name='auth_login'),
    url(r'logout/', AuthLogoutView.as_view(), name='auth_logout'),
    url(r'register/', RegisterView.as_view(), name='auth_register'),
    re_path(r'^register-validate/(?P<rand_str>[a-zA-Z0-9-_]+)/$',
            RegisterValidateView.as_view(), name='auth_register_validate'),
    url(r'forgot-password/',
        ForgotPasswordView.as_view(), name='auth_forgot_password'),
    re_path(r'password-reset/(?P<rand_str>[a-zA-Z0-9-_]+)/$',
            PasswordResetView.as_view(), name='auth_password_reset'),
    # endregion - auth URLs -

    # region - Django (not used: officially not finished) register / login -
    # Django has not finished the whole register / login process
    # that's why I've stopped trying to use it and I've implemented my own:
    # path('accounts/', include('django.contrib.auth.urls')),
    # url(r'accounts/password_change/', name='password_change'),
    # url(r'accounts/password_change/done/', name='password_change_done'),
    # url(r'accounts/password_reset/', name='password_reset'),
    # url(r'accounts/password_reset/done/', name='password_reset_done'),
    # url(r'accounts/reset/<uidb64>/<token>/', name='password_reset_confirm'),
    # url(r'accounts/reset/done/', name='password_reset_complete'),
    # endregion

    url(r'^new/$',                  NewIndexView.as_view(),              name='app_new_index'),
    url(r'^n/buttons$',             NewButtonsView.as_view(),            name='app_new_buttons'),
    url(r'^n/cards$',               NewCardsView.as_view(),              name='app_new_cards'),
    url(r'^n/utilities/color$',     NewUtilitiesColorView.as_view(),     name='app_new_utilities_color'),
    url(r'^n/utilities/border$',    NewUtilitiesBorderView.as_view(),    name='app_new_utilities_border'),
    url(r'^n/utilities/animation$', NewUtilitiesAnimationView.as_view(), name='app_new_utilities_animation'),
    url(r'^n/utilities/other$',     NewUtilitiesOtherView.as_view(),     name='app_new_utilities_other'),
    url(r'^n/404',                  New404View.as_view(),                name='app_new_404'),
    url(r'^n/blank',                NewBlankView.as_view(),              name='app_new_blank'),
    url(r'^n/charts',               NewChartsView.as_view(),             name='app_new_charts'),
    url(r'^n/tables',               NewTablesView.as_view(),             name='app_new_tables'),

    url(r'^$', IndexView.as_view(), name='app_index'),
    url(_(r'^wizards/?$'), WizardsIndexView.as_view(), name='app_wizards'),
    url(_(r'^wizard/?$'), WizardIndexView.as_view(), name='app_wizard_main'),
    url(_(r'^wizard/new-examination-template/?$'),
        WizardNewExamTemplateView.as_view(), name='wz_new_exam_template'),
    url(_(r'^wizard/new-exam/?$'),
        WizardNewExamView.as_view(), name='wz_new_exam'),
    url(_(r'^wizard/new-learners-group/?$'),
        WizardNewLearnersGroupView.as_view(), name='wz_new_learners_group'),

    url(r'^old$', OldIndexView.as_view(), name='app_old_index'),
    url(_(r'^interrogation/(?P<slug>[^/.]+)/$'),
        InterrogationDetailView.as_view(), name='app_interrogation'),
    url(_(r'^interrogations/$'),
        InterrogationListView.as_view(), name='app_interrogations'),
    url(_(r'^sessions/$'),
        SessionListView.as_view(), name='app_sessions'),
    url(_(r'^session/(?P<pk>[0-9]+)/$'),
        PersonneSessionDetailView.as_view(), name='app_person_session'),

    # region - wizard views -
    path(r'json/wz/step/<slug:uuid>/<slug:company>',
         WizardJsonStepView.as_view(), name='wizard_json_step'),
    path(r'json/wz/reset/<slug:uuid>/<slug:company>',
         WizardJsonResetView.as_view(), name='wizard_json_reset'),
    path(r'json/wz/cancel/<slug:uuid>/<slug:company>',
         WizardJsonCancelView.as_view(), name='wizard_json_cancel'),
    path(r'json/wz/goto/<slug:uuid>/<slug:company>',
         WizardJsonGotoView.as_view(), name='wizard_json_goto'),
    path(r'json/wz/help/<slug:company>',
         WizardJsonHelpView.as_view(), name='wizard_json_help'),
    # endregion - wizard views -
)
