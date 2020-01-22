import copy

from django import forms
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from social_django.models import UserSocialAuth

from app.admin.generic import HTMLAudioAdmin, CollapsedStackedInline, \
    ModelBullesAdmin, html_audio, action_mot_set_important, \
    action_mot_set_pas_important, \
    action_psp_mot_marquer_corrige_et_ok, action_psp_mot_marquer_corrige_et_faux
from app.forms.voix import VoixForm
from app.models.access_right import AccessRight
from app.models.bulle import GroupeBulle, Bulle, GroupeBulles
from app.models.categorie import CategoryLink, GroupeCategoriesReglesRegle, \
    CategoriesGroup, GroupeCategoriesRegles, Category
from app.models.entity.base import EntityLink, EntityAddress, EntityPhone
from app.models.entity.entities_group import EntitiesGroup
from app.models.entity.entities_group_type import EntitiesGroupType
from app.models.entity.person import Person
from app.models.interrogation import Interrogation, InterrogationPerson
from app.models.langue import Langue
from app.models.modele import ModeleInterrogationPhrase, \
    ModeleInterrogationGroupExpressions, ModeleInterrogation, ModeleSession
from app.models.expression import Expression, ExpressionVoice, \
    MotGroupeCategories, GroupExpressions
from app.models.personne_session import PersonneSession, \
    PersonneSessionPhrase, PersonneSessionPhraseMot
from app.models.phrase import Phrase, PhraseGroupeCategories
from app.models.regle import Regle
from app.models.voix import Voix, Fusion
from wizard.models.wz_user_step import WzUserStep


class QuerySetFilteredMixin(object):

    def queryset(self, request):
        """
        Filter the objects displayed in the change_list to only
        display those for the currently signed in user.
        :param request: request
        """
        qs = super().queryset(request)
        return qs.filter(owner=request.user)


class VoixAdmin(HTMLAudioAdmin):

    form = VoixForm
    readonly_fields = ('user', 'html_audio',)
    fields = ('user', 'description', 'fichier_audio', 'html_audio',
              'fusion_avec_suivant')
    list_display = ('description', 'html_audio', 'user')
    list_display_links = list_display
    search_fields = ['description']

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()


class BulleAdmin(admin.ModelAdmin):

    def list_bulles(self, obj):
        return format_html('{} - {} ({})'.format(obj.to_html(), obj.description,
                                                 obj.color))
    list_bulles.short_description = _('Groups of bubbles')
    list_bulles.allow_tags = True

    fields = ('description', 'color', 'contour')
    list_display = ('list_bulles', 'description', 'id', 'color')
    list_display_links = ('list_bulles', 'description', 'id', 'color')
    search_fields = ['description']


class GroupeBullesInline(CollapsedStackedInline):
    model = GroupeBulle
    fk_name = 'groupe'
    extra = 0
    verbose_name = _("Bubble")
    verbose_name_plural = _("Bubbles")


class GroupeBullesAdmin(admin.ModelAdmin):

    def list_bulles(self, obj):
        a = obj.bulles_html()
        return format_html('{}{}'.format('{} - '.format(a) if a != '' else '',
                                         obj.description))
    list_bulles.short_description = _('Groups of bubbles')
    list_bulles.allow_tags = True

    fields = ('description',)
    inlines = (GroupeBullesInline, )
    list_display = ('list_bulles', 'description', 'id')
    list_display_links = ('list_bulles', 'id', 'description')
    search_fields = ['description']


class CategorieLiensInline(CollapsedStackedInline):
    model = CategoryLink
    fk_name = 'src'
    extra = 0
    verbose_name = _("Parent")
    verbose_name_plural = _("Parents")


class CategorieAdmin(ModelBullesAdmin):

    fields = ('description', 'exemple', 'reference', 'groupe_bulles')
    inlines = (CategorieLiensInline, )
    list_display = ('list_bulles', 'description', 'exemple', 'reference', 'id')
    list_display_links = ('id', 'description', 'exemple')
    search_fields = ['description', 'exemple']
    # (!) change le bouton "Ajouter un nouveau" par "En tant que nouveau"
    save_as = True


class GroupeCategoriesReglesReglesInline(CollapsedStackedInline):
    model = GroupeCategoriesReglesRegle
    fk_name = 'groupecategoriesregles'
    raw_id_fields = ('groupecategoriesregles', 'regle')
    fields = ('groupecategoriesregles', 'regle')
    extra = 0
    verbose_name = ''
    verbose_name_plural = _("Rules")


class GroupeCategoriesReglesAdmin(admin.ModelAdmin):

    raw_id_fields = ('categoriesgroup_1', 'categoriesgroup_2',)
    inlines = (GroupeCategoriesReglesReglesInline,)
    # (!) change le bouton "Ajouter un nouveau" par "En tant que nouveau"
    save_as = True


class RegleAdmin(admin.ModelAdmin):

    def resume(self, obj):
        return _('{}').format(str(obj))
    resume.allow_tags = True
    resume.short_description = _('Summary')

    def exemple(self, obj):
        if obj is None:
            return ''
        return _('{} -> {}').format(
            obj.exemple_src if obj.exemple_src is not None else _('(?)'),
            obj.exemple_dst if obj.exemple_dst is not None else _('(?)'),
        )
    exemple.allow_tags = True
    exemple.short_description = _('Example')

    fieldsets = (
        (None, {
            'fields': (('description',),
                       ('exemple_src',),
                       ('exemple_dst',),),
        }),
        (_('Current word'), {
            'fields': (('mot_courant_regle',),
                       ('mot_courant_filtre',),
                       ('mot_courant_filtre_est_lettre',),
                       ('mot_courant_case_insensible',),),
        }),
        (_('Next word'), {
            'fields': (('mot_suivant_regle',),
                       ('mot_suivant_filtre',),
                       ('mot_suivant_filtre_est_lettre',),
                       ('mot_suivant_case_insensible',),),
        }),
        (_('Replacing word'), {
            'fields': (('mot_remplacant',),),
        }),
    )
    raw_id_fields = ('mot_remplacant', )
    list_display = ('resume', 'exemple', )
    list_display_links = list_display
    search_fields = ['description']
    # (!) change le bouton "Ajouter un nouveau" par "En tant que nouveau"
    save_as = True


class MotGroupeCategoriesInline(CollapsedStackedInline):
    model = Expression.categories_groups.through
    fk_name = 'expression'
    fields = ('group_categories',)
    extra = 0
    verbose_name = _("Group of categories")
    verbose_name_plural = _("Groups of categories")


class MotVoiceInline(CollapsedStackedInline):
    model = ExpressionVoice
    fk_name = 'expression'
    fields = ('expression', 'voix')
    extra = 0
    verbose_name = _("Voice")
    verbose_name_plural = _("Voices")


class MotAdmin(QuerySetFilteredMixin, admin.ModelAdmin):

    def html_audio_mot(self, obj):
        if obj:
            return format_html('<br/>'.join([
                html_audio(reverse('url_public', args={v.fichier_audio}))
                for v in obj.voix.all()]))
    html_audio_mot.short_description = _('Word alone')
    html_audio_mot.allow_tags = True

    def get_search_results(self, request, queryset, search_term):
        return super(MotAdmin, self).get_search_results(request, queryset,
                                                        search_term)

    def est_important(self, obj):
        if obj.important:
            return format_html('&#x2605;')
        return format_html('&#x22C5;')
    est_important.allow_tags = True
    est_important.short_description = _('I.')

    def has_voix(self, obj):
        if len(obj.voices.all()):
            return format_html('&#x2714;')
        return format_html('&#x22C5;')
    has_voix.allow_tags = True
    has_voix.short_description = _('V.')

    readonly_fields = ('expression_with_categories', 'html_audio_mot')

    fieldsets = (
        (None, {
            'fields': ('texte', 'exemple', 'reference', 'important',
                       'html_audio_mot',)
        }),
        (_("Automatic generation"), {
            'classes': ('collapse',),
            'fields': ('generate_voice', 'generate_voice_language',),
        }),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': ('date_v_start', 'date_v_end'),
        }),
    )
    inlines = (MotGroupeCategoriesInline, MotVoiceInline)
    list_display = ('texte', 'est_important', 'has_voix',
                    'expression_with_categories', 'date_last_modif',
                    'generate_voice', 'generate_voice_language', 'id')
    list_display_links = list_display
    list_per_page = 200
    actions = [action_mot_set_important,
               action_mot_set_pas_important]
    search_fields = ['^texte', ]
    # (!) "Enregistrer et ajouter un nouveau" devient "En tant que nouveau"
    save_as = True


class MotGroupeCategoriesAdmin(admin.ModelAdmin):

    def mot_texte(self, obj):
        return obj.expression.texte
    mot_texte.allow_tags = True
    mot_texte.short_description = _('I.')

    raw_id_fields = ('expression', 'group_categories')
    list_display = ('group_categories', 'mot_texte', 'id')
    list_display_links = list_display
    search_fields = ['group_categories__description']


class CategoriesGroupCategoriesInline(CollapsedStackedInline):
    model = CategoriesGroup.links.through
    fk_name = 'group_categories'
    raw_id_fields = ('category',)
    # fields = ('group_categories', 'category')
    extra = 0
    verbose_name = _("Category")
    verbose_name_plural = _("Categories")


class GroupeCategoriesForm(forms.ModelForm):
    e = {'required': _('This field is required'),
         'invalid': _('This field contains invalid data')}

    a = _('Description:')
    description = forms.CharField(
        label=a, max_length=100,
        widget=forms.TextInput(attrs={'title': a, 'size': 100, 'type': 'text',
                                      'placeholder': _('description'),
                                      'class': 'form-control'}),
        error_messages=e)

    a = _('Example:')
    exemple = forms.CharField(
        label=a, max_length=100,
        widget=forms.TextInput(attrs={'title': a, 'size': 100, 'type': 'text',
                                      'placeholder': _('example'),
                                      'class': 'form-control'}),
        error_messages=e)

    def __init__(self, *args, **kwargs):
        super(GroupeCategoriesForm, self).__init__(*args, **kwargs)
        # only change attributes if an instance is passed
        # instance = kwargs.get('instance')
        # if instance:
        #     u = User.objects.get(pk=instance.user.pk)
        #     self.base_fields['user_first_name'].initial = u.first_name
        #     self.base_fields['user_last_name'].initial = u.last_name
        #     self.base_fields['user_email'].initial = u.email

    class Meta:
        model = CategoriesGroup
        fields = ('description', 'exemple')


class GroupeCategoriesAdmin(admin.ModelAdmin):
    form = GroupeCategoriesForm
    fields = ('description', 'exemple',)

    list_display = ('description', 'exemple', 'id')
    list_display_links = list_display
    list_per_page = 200
    search_fields = ['description', 'links__description']
    # (!) change le bouton "Ajouter un nouveau" par "En tant que nouveau"
    save_as = True

    inlines = (CategoriesGroupCategoriesInline,)

    verbose_name = _("Group of categories")
    verbose_name_plural = _("Categories: groups of categories")


class GroupeExpressionsAdmin(admin.ModelAdmin):

    def all_expressions(self, obj):

        def wrap_span(txt):
            return format_html('<span style="font-family:courier; '
                               'font-weight:bolder">{}</span>'.format(txt))

        def info(mm):
            return format_html('<a href="{}">{}</a>'
                               ' - {}'.format(reverse('admin:app_mot_change',
                                                      args=(mm.pk,)),
                                              mm.texte, str(mm.pk)))
        if obj.pk is None:
            return ''
        t = obj.expressions.all().order_by('texte')
        a = '<br />'.join([wrap_span('X&nbsp;/ ')+info(m)
                           for m in t if m.important])
        b = '<br />'.join([wrap_span('.&nbsp;/ ')+info(m)
                           for m in t if not m.important])
        return format_html('{}{}{}'.format(a, '<br />' if a and b else '', b))
    all_expressions.allow_tags = True
    all_expressions.short_description = _('Current words')

    readonly_fields = ('all_expressions',)

    raw_id_fields = ('expressions', )

    verbose_name = _("Group")
    verbose_name_plural = _("Groups of expressions")


class PhraseGroupesCategoriesInline(CollapsedStackedInline):
    model = Phrase.categories_groups.through
    fk_name = 'phrase'
    fields = ('ordre', 'phrase', 'group_categories', )
    extra = 0
    verbose_name = _("Group of categories")
    verbose_name_plural = _("Groups of categories")


class PhrasesForm(forms.ModelForm):
    e = {'required': _('This field is required'),
         'invalid': _('This field contains invalid data')}

    a = _('Description:')
    description = forms.CharField(
        label=a, max_length=100,
        widget=forms.TextInput(attrs={
            'title': a, 'size': 100, 'type': 'text',
            'placeholder': _('description'),
            'class': 'form-control'}),
        error_messages=e)

    a = _('Example:')
    exemple = forms.CharField(
        label=a, max_length=100, required=False,
        widget=forms.TextInput(attrs={
            'title': a, 'size': 100, 'type': 'text',
            'placeholder': _('example'),
            'class': 'form-control'}),
        error_messages=e)

    class Meta:
        model = Phrase
        fields = ('description', 'exemple')


class PhraseAdmin(admin.ModelAdmin):
    form = PhrasesForm
    fields = ('description', 'exemple', 'duree_silence_debut',
              'duree_silence_fin')
    inlines = (PhraseGroupesCategoriesInline,)
    list_display = ('description', 'exemple', 'id')
    list_display_links = list_display


class ModeleInterrogationPhrasesInline(CollapsedStackedInline):
    model = ModeleInterrogationPhrase
    fk_name = 'interrogation'
    raw_id_fields = ('phrase',)
    fields = ('importance', 'phrase')
    extra = 0
    verbose_name = _("Sentence")
    verbose_name_plural = _("Sentences")


class ModeleInterrogationGroupExpressionsInline(CollapsedStackedInline):
    model = ModeleInterrogationGroupExpressions
    fk_name = 'interrogation'
    fields = ('groupe_groupe_expressions', )
    extra = 0
    verbose_name = _("Group of expressions")
    verbose_name_plural = _("Groups of expressions")


class ModeleInterrogationAdmin(ModelBullesAdmin):

    def list_bulles_more(self, obj):
        a = self.list_bulles(obj)
        return '{}{}'.format(a+' - ' if a != '' else '', obj.description)
    list_bulles_more.allow_tags = True
    list_bulles_more.short_description = _('Col.')

    fields = ('description', 'groupe_bulles')
    inlines = (ModeleInterrogationPhrasesInline,
               ModeleInterrogationGroupExpressionsInline)
    list_display = ('list_bulles_more', 'id', 'description')
    list_display_links = list_display
    search_fields = ['description']
    # (!) change le bouton "Enregistrer et ajouter un nouveau" par "E
    save_as = True


class InterrogationPersonsInline(CollapsedStackedInline):
    model = InterrogationPerson
    fk_name = 'interrogation'
    fields = ('interrogation', 'person')
    extra = 0
    verbose_name = _("person")
    verbose_name_plural = _("persons")


class InterrogationSessionsInline(CollapsedStackedInline):
    model = PersonneSession
    fk_name = 'interrogation'
    fields = ('modele', )
    extra = 0
    verbose_name = _("session")
    verbose_name_plural = '{} ({}, {}, {})'.format(
            _("sessions"), _("for consulting ONLY"),
            _("DO NOT TOUCH"),
            _("they are automatically generated"))


class InterrogationAdmin(ModelBullesAdmin):
    fields = ('user', 'groupe_bulles', 'description', 'modele')
    list_display = ('list_bulles', 'description', 'id', 'date_last_modif')
    list_display_links = list_display
    search_fields = ['description']
    inlines = (InterrogationPersonsInline, InterrogationSessionsInline)
    # (!) change le bouton "Enregistrer et ajouter un nouveau" par "
    save_as = True


class ModeleSessionAdmin(ModelBullesAdmin):
    fields = ('description', 'total', 'max_duration')
    list_display = ('description', 'max_duration', 'total',
                    'id', 'date_last_modif')
    list_display_links = list_display
    search_fields = ['description']


class EntityLinksAdmin(CollapsedStackedInline):
    model = EntityLink
    fk_name = 'src'
    fields = ('src', 'link_type', 'dst')
    extra = 0
    verbose_name = _("Relation")
    verbose_name_plural = _("Relations")


class EntityAddressesAdmin(CollapsedStackedInline):
    model = EntityAddress
    fk_name = 'entity'
    fields = ('address', 'address_type')
    extra = 0
    verbose_name = _("Address")
    verbose_name_plural = _("Addresses")


class EntityPhonesAdmin(CollapsedStackedInline):
    model = EntityPhone
    fk_name = 'entity'
    fields = ('phone', 'phone_type')
    extra = 0
    verbose_name = _("Phone")
    verbose_name_plural = _("Phones")


class PersonAdmin(ModelBullesAdmin):

    def get_user(self, obj):
        return str(obj)
    get_user.allow_tags = True
    get_user.short_description = _('Person')

    def gravatar_img(self, obj):
        return format_html('<img src={} />'.format(obj.gravatar_cached_image()))
    gravatar_img.allow_tags = True
    gravatar_img.short_description = _('Gravatar image')

    def is_active(self, obj):
        return format_html(
            '<span style="font-size: 3vh; vertical-align:center">'
            '{}'
            '</span>'.format('&#9745;' if obj.user.is_active else '&#9744;'))
    is_active.allow_tags = True
    is_active.short_description = _('Activated')

    fields = ('user', 'gravatar', 'confirmation_code', 'reset_code')
    list_display = ('list_bulles', 'is_active', 'gravatar_img', 'get_user',
                    'id',)
    list_display_links = list_display
    inlines = (EntityLinksAdmin, EntityAddressesAdmin, EntityPhonesAdmin)


class PeopleSessionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('personne', 'modele', 'interrogation',)
        }),
        (_("Advanced options"), {
            # 'classes': ('collapse',),
            'fields': ('date_v_start', 'date_v_end'),
        }),
    )
    list_display = ('__str__', 'personne', 'modele', 'interrogation', 'id')
    list_display_links = list_display


class PeopleSessionPhraseAdmin(HTMLAudioAdmin):
    def lien_vers_interrogation(self, obj):
        if obj:
            return format_html('<a href="{}" target="_blank">{}</a>'.format(
                reverse('admin:app_interrogation_change',
                        args=(obj.ps.interrogation.pk,), ), _('See')))
    lien_vers_interrogation.short_description = _("Interrogation")
    lien_vers_interrogation.allow_tags = True

    def lien_vers_session(self, obj):
        if obj:
            return format_html('<a href="{}" target="_blank">{}</a>'.format(
                reverse('admin:app_person_session_change',
                        args=(obj.ps.pk,), ), _("See")))
    lien_vers_session.short_description = _("Session")
    lien_vers_session.allow_tags = True

    readonly_fields = ('html_audio', 'lien_vers_interrogation',
                       'lien_vers_session',)
    fieldsets = (
        (None, {
            'fields': ('ps', 'phrase', 'html_audio')
        }),
        (_('Parent links'), {
            'fields': ('lien_vers_interrogation', 'lien_vers_session',)
        }),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': ('date_v_start', 'date_v_end'),
        }),
    )


class PersonneSessionPhraseMotAdmin(admin.ModelAdmin):

    def html_audio_phrase(self, obj):
        if obj and obj.psp:
            return format_html(html_audio(reverse(
                'url_public', args={obj.psp.fichier_audio})))

    html_audio_phrase.short_description = _('Full sentence')
    html_audio_phrase.allow_tags = True

    def html_audio_mot(self, obj):
        if obj and obj.mot:
            return format_html('<br/>'.join([
                html_audio(reverse('url_public',
                                   args={v.fichier_audio}))
                for v in obj.mot.voix.all()]))
    html_audio_mot.short_description = _('Word alone')
    html_audio_mot.allow_tags = True

    def lien_vers_psp(self, obj):
        if obj:
            return format_html('<a href="{}" target="_blank">{}</a>'.format(
                reverse('admin:app_personnesessionphrase_change',
                        args=(obj.psp.pk,), ), _('See')))
    lien_vers_psp.short_description = _('Person session sentence')
    lien_vers_psp.allow_tags = True

    def est_important(self, obj):
        if obj and obj.mot:
            if obj.mot.important:
                return format_html('&#x2605;')
            return format_html('&#x22C5;')
        return '?'
    est_important.allow_tags = True
    est_important.short_description = _('I.')

    readonly_fields = ('lien_vers_psp', 'html_audio_phrase', 'html_audio_mot')
    fieldsets = (
        (None, {
            'fields': ('psp', 'mot', 'ordre', 'etat', 'lien_vers_psp')
        }),
        (_('Correction'), {
            # 'classes': ('collapse',),
            'fields': ('correcteur', 'date_correction', 'est_valide'),
        }),
        (_('Audio'), {
            # 'classes': ('collapse',),
            'fields': ('html_audio_phrase', 'html_audio_mot'),
        }),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': ('date_v_start', 'date_v_end'),
        }),
    )
    raw_id_fields = ('mot', )
    list_display = ('est_important', 'etat', 'est_valide', 'mot', 'psp',
                    'ordre', 'id')
    list_display_links = list_display
    actions = [action_psp_mot_marquer_corrige_et_ok,
               action_psp_mot_marquer_corrige_et_faux]


class MyAdminSite(AdminSite):
    site_header = _("Interro / administration")

    models_on_top = ['Entity', 'Person', 'EntitiesGroup', 'EntitiesGroupType',
                     'EntityLink']

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request)

        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        if len(app_list):
            # ! custom sort:
            el = copy.deepcopy(app_list[0])
            el['models'] = [a for a in el['models']
                            if a['object_name'] in self.models_on_top]
            app_list[0]['models'] = [
                a for a in app_list[0]['models']
                if a['object_name'] not in self.models_on_top]
            el['name'] = _("Frequently needed")
            app_list.insert(0, el)

        return app_list


my_admin_site = MyAdminSite(name='my_admin')
my_admin_site.register(AccessRight)
my_admin_site.register(Bulle, BulleAdmin)
my_admin_site.register(GroupeBulles, GroupeBullesAdmin)
my_admin_site.register(Langue)
my_admin_site.register(Fusion)

# region - models for interrogation -
my_admin_site.register(Expression, MotAdmin)
my_admin_site.register(MotGroupeCategories, MotGroupeCategoriesAdmin)
my_admin_site.register(GroupeCategoriesRegles, GroupeCategoriesReglesAdmin)
my_admin_site.register(CategoriesGroup, GroupeCategoriesAdmin)
my_admin_site.register(GroupExpressions, GroupeExpressionsAdmin)
my_admin_site.register(ModeleInterrogation, ModeleInterrogationAdmin)
my_admin_site.register(ModeleSession, ModeleSessionAdmin)
my_admin_site.register(Interrogation, InterrogationAdmin)
my_admin_site.register(Phrase, PhraseAdmin)
my_admin_site.register(PhraseGroupeCategories)
my_admin_site.register(Category, CategorieAdmin)
my_admin_site.register(Regle, RegleAdmin)
my_admin_site.register(Voix, VoixAdmin)
# endregion - models for interrogation -

my_admin_site.register(EntityLink)
my_admin_site.register(EntityPhone)
my_admin_site.register(EntityAddress)
my_admin_site.register(EntitiesGroup)
my_admin_site.register(EntitiesGroupType)
my_admin_site.register(Person, PersonAdmin)
my_admin_site.register(PersonneSession, PeopleSessionAdmin)
my_admin_site.register(PersonneSessionPhrase, PeopleSessionPhraseAdmin)
my_admin_site.register(PersonneSessionPhraseMot, PersonneSessionPhraseMotAdmin)

my_admin_site.register(WzUserStep)

my_admin_site.register(Group)
my_admin_site.register(User)
my_admin_site.register(UserSocialAuth)
