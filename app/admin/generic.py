# Toutes mes classe génériques de l'administration
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from app.models.personne_session import PersonneSessionPhraseMot
from django.contrib import admin


class CollapsedStackedInline(admin.StackedInline):
    class Media:
        css = {
            # 'all': ('pretty.css',)
        }
        js = ('js/vendor/jquery/3.4.1/jquery.min.js',
              'js/admin/collapsed_stacked_inlines.js',)


class BigSelectMultiplesAdmin(admin.ModelAdmin):
    class Media:
        css = {
        }
        js = ('js/vendor/jquery/3.4.1/jquery.min.js',
              'js/admin/big_select_multiples.js',)


class ResizableAdmin(admin.ModelAdmin):
    """
    Les multi select sont hyper petits.
    Ici, solution appliquée dans l'interface d'admin :
    - champ "int" sur lequel on met la classe "resize_src" et un autre champ
    - autre champ sur lequel on met la classe "resize_dst"

    -> en jQuery, je redimensionne "resize_dst" dès que "resize_src" change.
    """
    class Media:
        css = {
        }
        js = ('js/vendor/jquery/3.4.1/jquery.min.js',
              'js/admin/resize_widgets.js',)


def html_audio(url):
    return '<audio controls><source src="{}" type="audio/mp3">{}' \
           '</audio>'.format(url, _("Your web browser can't read audio files."))


class HTMLAudioAdmin(admin.ModelAdmin):
    def html_audio(self, obj):
        if obj:
            return format_html(
                html_audio(reverse('url_public', args={obj.fichier_audio})))
    html_audio.short_description = _("Audio")
    html_audio.allow_tags = True


class ModelBullesAdmin(admin.ModelAdmin):

    def list_bulles(self, obj):
        if not obj.groupe_bulles:
            return ''
        a = format_html(obj.groupe_bulles.bulles_html())
        return a if a != '' else ''
    list_bulles.allow_tags = True
    list_bulles.short_description = _('Col.')


def action_mot_set_value(queryset, b):
    queryset.update(important=b)


def action_mot_set_important(model_admin, request, queryset):
    action_mot_set_value(queryset, True)


action_mot_set_important.short_description = \
    _("Check as IMPORTANT for an interrogation")


def action_mot_set_pas_important(model_admin, request, queryset):
    action_mot_set_value(queryset, False)


action_mot_set_pas_important.short_description = \
    _("Check as NOT important for an interrogation")


def action_psp_mot_marquer_corrige_et(queryset, est_bien_ecrit):
    queryset.update(etat=PersonneSessionPhraseMot.ETAT_CORRIGE,
                    date_correction=timezone.now(),
                    est_valide=est_bien_ecrit)


def action_psp_mot_marquer_corrige_et_ok(model_admin, request, queryset):
    action_psp_mot_marquer_corrige_et(queryset, True)


action_psp_mot_marquer_corrige_et_ok.short_description = \
    _("Check as verified and OK")


def action_psp_mot_marquer_corrige_et_faux(model_admin, request, queryset):
    action_psp_mot_marquer_corrige_et(queryset, False)


action_psp_mot_marquer_corrige_et_faux.short_description = \
    _("Check as verified and NOT ok")

