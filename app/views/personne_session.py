import collections
import os
import random
import shutil
import tempfile
import uuid
from os.path import join

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from os.path import abspath

from pydub import AudioSegment

from evalr.settings import MEDIA_ROOT
from app.models.categorie import GroupeCategoriesRegles
from app.models.personne_session import PersonneSession, \
    PersonneSessionPhrase, PersonneSessionPhraseMot
from app.models.phrase import PhraseGroupeCategories
from app.models.voix import AudioSegmentCustom


class PersonneSessionDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'personnesession_detail.html'
    model = PersonneSession
    slug_field = 'pk'

    def get_context_data(self, **kwargs):

        def local_uniq(obj):
            w = obj.date_last_modif
            return '%09d-%02d-%02d-%04d-%02d:%02d:%02d-%08d' % \
                   (obj.pk, w.day, w.month, w.year, w.hour, w.minute,
                    w.second, w.microsecond)

        context = super().get_context_data(**kwargs)
        if self.object is None:
            return context

        # S'assurer que la session demandée est bien à l'utilisateur connecté :
        a = PersonneSession.objects.filter(
                personne__user=self.request.user,
                modele=self.object.modele)
        if not len(a):
            context['errors'] = {
                'session': {
                    'titles': [(_("This session isn't yours"),)],
                    'list': [(_("Try a session that is yours"),)]},
                'no_group': {'titles': [], 'list': []},
                'no_voice': {'titles': [], 'list': []},
                'aucune_phrase_dst': {'titles': [], 'list': []}
            }
            return context

        # On regarde si on a déjà calculé les phrases + mots dans la base de
        # données.
        # Lorsqu'on calcule les phrases et les mots, on écrit tout en base
        # via PersonneSessionPhrase et PersonneSessionPhraseMot
        # -> regarder si on en a au moins un :
        session_phrases = PersonneSessionPhrase.objects.filter(ps=self.object)
        if not len(session_phrases):
            # On n'a pas encore généré de phrase -> creer_phrases()
            # -> boucle sur le retour qui est soit phrases soit erreur :
            for k, v in self.creer_phrases().items():
                context[k] = v
            if context.get('errors', None):
                return context

        # Arrivé ici dans tous les cas les phrases sont forcément générées
        # -> Vérifier si les mp3 "fusionnés" sont là, sinon les créer :
        session_phrases = PersonneSessionPhrase.objects.filter(
                ps=self.object)
        for sp in session_phrases:
            if sp.fichier_audio:
                full_name = abspath(join(MEDIA_ROOT, str(sp.fichier_audio)))
                if os.path.isfile(full_name):
                    continue
            session_phrase_mots = PersonneSessionPhraseMot.objects\
                .filter(psp=sp).order_by('ordre')
            # Répertoire destination du wav =
            # grosse chaîne concaténée de id + date_last_modif de :
            # (phrase mot de la session) + tous les wav de ses mots associés
            # comme ça dès qu'un wav est modifié, l'uniqu id change et
            # donc, en théorie, le nom destination aussi.
            uniq = local_uniq(sp)
            mp3s = []
            for s_p_m in session_phrase_mots:
                for v in s_p_m.mot.voices.all():
                    mp3s.append(str(v.fichier_audio.file))
                    uniq += local_uniq(v)
            nom = str(uuid.uuid5(uuid.NAMESPACE_OID, uniq))+'.mp3'

            # Ex: dst = "play/bea536a0/089c/51a3/8c0e/beeb00f2a45b.mp3"
            dst = 'play/'+'/'.join(nom.split('-'))

            # Ex: "C:\Users\...\play\bea536a0\089c\51a3\8c0e\beeb00f2a45b.mp3"
            dst_full = abspath(join(MEDIA_ROOT, dst))

            # Ex: "C:\Users\...\play\bea536a0\089c\51a3\8c0e"
            dst_base = os.path.dirname(dst_full)
            if not os.path.exists(dst_base):
                os.makedirs(dst_base)

            # !!! TMP to force re-generation
            # if not os.path.isfile(dst_full):
            if True:
                # Générer le fichier
                prev_crossfade_length = None
                final = None
                prev_mot = ''
                for s_p_m in session_phrase_mots:
                    print('prev = {}, mot = {}'.format(prev_mot, s_p_m.mot))
                    voices = s_p_m.mot.voices.all()
                    voices = s_p_m.mot.get_voices(user=self.request.user)
                    for v in voices:
                        mp3_src = str(v.fichier_audio.file)
                        if final is None:
                            final = AudioSegmentCustom.from_mp3(mp3_src)
                        else:
                            audio_s = AudioSegmentCustom.from_mp3(mp3_src)
                            if prev_crossfade_length is not None:
                                print('cross fade!!!')
                                final = final.fade_override(
                                            audio_s,
                                            fade_len=min(prev_crossfade_length,
                                                         len(audio_s),
                                                         len(final)))
                            else:
                                final = final + audio_s
                        f = v.fusion_avec_suivant
                        prev_mot = s_p_m.mot
                        # if f and f.duree_crossfade is not None:
                        #     prev_crossfade_length = f.duree_crossfade
                        # else:
                        prev_crossfade_length = None
                if final is None:
                    raise ValidationError(_("No voice to generate"))
                out_f = open(dst_full, 'wb')
                final.export(out_f, format='mp3')
                out_f.close()
                # -> Voix pour la phrase fait, ajouter petit son début + fin car
                # sur phrases courtes = sons courts, les lecteurs
                # ne fonctionnent pas bien :
                deb = sp.phrase.duree_silence_debut
                if deb is not None:
                    fhandle, tmp_name = tempfile.mkstemp(suffix='.tmp.mp3')
                    os.close(fhandle)
                    os.chmod(tmp_name, 0o777)
                    final = AudioSegment.silent(float(deb * 1000))
                    final = final + AudioSegment.from_mp3(dst_full)
                    out_f = open(tmp_name, 'wb')
                    final.export(out_f, format='mp3')
                    out_f.close()
                    os.remove(dst_full)
                    if os.path.isfile(dst_full):
                        raise ValidationError(_("File deletion error"))
                    # ! shutil.move() much powerful than os.rename() -> use it:
                    shutil.move(tmp_name, dst_full)
                    if not os.path.isfile(dst_full):
                        raise ValidationError(_("File moving error"))

                # fin = Voix.cree_fichier_silence(sp.phrase.duree_silence_fin)
                fin = sp.phrase.duree_silence_fin
                if fin is not None:
                    fhandle, tmp_name = tempfile.mkstemp(suffix='.tmp.mp3')
                    os.close(fhandle)
                    os.chmod(tmp_name, 0o777)
                    final = AudioSegment.from_mp3(dst_full)
                    final = final + AudioSegment.silent(float(fin * 1000))
                    out_f = open(tmp_name, 'wb')
                    final.export(out_f, format='mp3')
                    out_f.close()
                    os.remove(dst_full)
                    if os.path.isfile(dst_full):
                        raise ValidationError(_("File deletion error"))
                    # ! shutil.move() much powerful than os.rename() -> use it:
                    shutil.move(tmp_name, dst_full)
                    if not os.path.isfile(dst_full):
                        raise ValidationError(_("File moving error"))

                sp.fichier_audio = dst
                sp.save()
        # Reconstruire toutes les phrases
        context['phrases'] = []
        for sp in session_phrases:
            context['phrases'].append('/public/' + str(sp.fichier_audio))

        return context

    def creer_phrases(self):

        def infos_rule(mm):
            return str(mm), reverse('admin:app_regle_change', args=(mm.pk,))

        def infos(mm):
            return str(mm), reverse('admin:app_mot_change', args=(mm.pk,))

        errors = {
            'no_group': {'titles': [], 'list': [], 'urls': []},
            'no_voice': {'titles': [], 'list': [], 'urls': []},
            'aucune_phrase_dst': {'titles': [], 'list': [], 'urls': []},
            'rules_problems': {'titles': [], 'list': [], 'urls': []}
        }
        result = {}

        # Retrouver toutes les phrases et les mots dont on a besoin.
        #
        # Récupérer le modèle d'interrogation pour récupérer phrases et mots :
        modele = self.object.interrogation.modele
        total_phrases_max = self.object.modele.total

        phrases_finales = []
        # Un modèle d'interrogation est composé de phrases + groupes de mots
        # (1) aller chercher la totalité des mots de tous les groupes de mots.
        # Aller chercher tous les mots de l'interrogation (= pas de la session
        # uniquement, mais l'interrogation totale) qui sont ok
        expressions_corrected_ok = [
            p['mot__pk'] for p in PersonneSessionPhraseMot.objects.filter(
                    psp__ps__interrogation=self.object.interrogation,
                    mot__important=True,
                    etat__exact=PersonneSessionPhraseMot.ETAT_CORRIGE,
                    est_valide=True).all().values('mot__pk')]
        expressions = {}
        important_expressions = 0
        for groupe_groupe_expressions in modele.groupes_mots.all():
            for mot in groupe_groupe_expressions.mots.all():
                if mot.pk in expressions_corrected_ok:
                    continue
                if not len(mot.voices.all()) and not mot.generate_voice:
                    errors['no_voice']['list'].append(infos(mot))
                mot_gc_all = mot.categories_groups.all()
                if not len(mot_gc_all):
                    errors['no_group']['list'].append(infos(mot))
                added = False
                for gc in mot_gc_all:
                    if not expressions.get(gc.pk, None):
                        expressions[gc.pk] = {'g': gc, 'mots': {}}
                    if not expressions[gc.pk]['mots'].get(mot.pk, None):
                        added = True
                        expressions[gc.pk]['mots'][mot.pk] = mot
                # N'incrémenter qu'au premier ajout :
                if added and mot.important:
                    important_expressions += 1

        if len(errors['no_voice']['list']):
            # make translation only here:
            errors['no_voice']['titles'].append(
                  _("The following words have no associated sound. "
                    "They can't be in an interrogation."))
            errors['no_voice']['titles'].append(
                _("&nbsp;&raquo; &raquo; there's a sound needed for:"))
        if len(errors['no_group']['list']):
            errors['no_group']['titles'].append(
                    _("Following words have no groups of categories. "
                      "They can't be used in a sentence."))
            errors['no_group']['titles'].append(
                    "&nbsp;&raquo; &raquo; {}:".format(
                        _("You have to associate at least one category:")))
        if len(errors['no_group']['list']) or len(errors['no_voice']['list']):
            result['errors'] = errors
            return result
        # -> expressions: it's sorted by "groups" in which they are

        # (2) fetch all possible phrases
        sentences = {}
        for mip in modele.modeleinterrogationphrase_set.all():
            if not sentences.get(mip.importance, None):
                sentences[mip.importance] = {}
            sentences[mip.importance][mip.phrase.pk] = mip.phrase
        # les re-trier par importance :
        sentences = collections.OrderedDict(sorted(sentences.items()))
        # -> ok dans phrases : toutes les phrases triées par importance

        while len(expressions) and len(sentences) and important_expressions:
            # Choose a random sentence in the most important (= the first):
            premiere = next(iter(sentences))
            # rnd = pk d'une phrase :
            rnd = random.choice(list(sentences[premiere]))

            # p = random sentence :
            p = sentences[premiere][rnd]

            # extract groups via manytomany sentence<->group:
            gc = [a.group_categories
                  for a in PhraseGroupeCategories.objects.filter(phrase=p)
                  .order_by('ordre')]

            phrase = []
            ok = True
            for a in gc:  # a = manytomany phrase<->groupe
                rnd_mots = expressions.get(a.pk, None)
                if rnd_mots:
                    rnd_mot = random.choice(list(expressions[a.pk]['mots']))
                    mot = expressions[a.pk]['mots'][rnd_mot]
                    phrase.append(mot)
                else:
                    # on n'a plus de mots qui font partie de ce groupe
                    # -> on ne peut pas construire ce type de phrase
                    del sentences[premiere][rnd]
                    if len(sentences[premiere]) == 0:
                        del sentences[premiere]
                    ok = False
                    break
            if ok:
                # phrase construite dans phrase[] -> l'ajouter :
                for mot in phrase:
                    if mot.important:
                        important_expressions -= 1
                        for gc in mot.categories_groups.all():
                            del expressions[gc.pk]['mots'][mot.pk]
                            if len(expressions[gc.pk]['mots']) == 0:
                                del expressions[gc.pk]
                phrases_finales.append({'phrase': p, 'mots': phrase})
                if len(phrases_finales) == total_phrases_max:
                    # court-circuiter pour tout arrêter :
                    important_expressions = 0

        if important_expressions == 0:
            # Ok ! Tous les mots importants ont été "éliminés" au fur et à
            # mesure de la construction des phrases, parfait !
            # Maintenant pour chaque mots des phrases construites,
            # appliquer les règles spéciales, exemple : "le homme" -> "l'homme"
            # Routine pour savoir si on est sur le dernier élément :
            # Pris en googlant "python for last" 1er résultat sur stackoverflow
            for p in phrases_finales:
                mot_prev = idx_prev = None
                for idx, mot in enumerate(p['mots']):
                    # appliquer avant de nettoyer les gc
                    if mot_prev:
                        for gcr in GroupeCategoriesRegles.objects.filter(
                            categoriesgroup_1__in=[
                                gc.pk
                                for gc in mot_prev.categories_groups.all()],
                            categoriesgroup_2__in=[
                                gc.pk
                                for gc in mot.categories_groups.all()]
                        ):
                            for r in gcr.regles.all():
                                if r.ok_with_mots(mot_prev, mot):
                                    if r.mot_remplacant is not None:
                                        print("on remplace {} par {}".format(
                                            str(p['mots'][idx_prev]),
                                            str(r.mot_remplacant)
                                        ))
                                        p['mots'][idx_prev] = r.mot_remplacant
                                    else:
                                        errors['rules_problems'] = {
                                            'titles': [
                                                _("A rule isn't properly setup"),
                                                _("There's one word missing "
                                                  "for this rule:")],
                                            'list': [infos_rule(r)]
                                        }
                                        result['errors'] = errors
                                        return result
                    mot_prev = mot
                    idx_prev = idx
            # Arrivé ici, tout est construit !
            # Dans phrases_finales on a un dictionnaire de
            # {'phrase': p, 'mots': phrase}.
            # "mots" = tableau de mots ordonnés
            # -> tout enregistrer en base de données
            for i, p in enumerate(phrases_finales):
                psp = PersonneSessionPhrase.objects.create(
                        ps=self.object, phrase=p['phrase'])
                psp.save()
                for j, mot in enumerate(p['mots']):
                    if type(mot) is list:
                        for m in mot:
                            spm = PersonneSessionPhraseMot.objects.create(
                                psp=psp, mot=m, ordre=j
                            )
                            spm.save()
                    else:
                        spm = PersonneSessionPhraseMot.objects.create(
                            psp=psp, mot=mot, ordre=j
                        )
                        spm.save()

            # Code pour remplacer chaque item par son équivalent "texte"
            for i, p in enumerate(phrases_finales):
                finale = []
                for j, mot in enumerate(p['mots']):
                    if type(mot) is list:
                        # liste quand on a appliqué une règle transformation,
                        # ça peut donner lieu à plusieurs mots = tableau
                        finale.append(' '.join([a if a is isinstance(a, str)
                                                else a.texte for a in mot]))
                    else:
                        finale.append(mot.texte)
                phrases_finales[i] = ' '.join(m for m in finale).capitalize()
        else:
            # Tous les mots ne sont pas casés dans des phrases
            # -> mauvaise organisation du prof
            important_expressions = {}
            for pk in expressions:
                for idx in expressions[pk]['mots']:
                    mot = expressions[pk]['mots'][idx]
                    if mot.important:
                        important_expressions[mot.pk] = mot
            for idx in important_expressions:
                m = important_expressions[idx]
                g = u', '.join([str(g) for g in m.categories_groups.all()])
                a, b = infos(m)
                errors['aucune_phrase_dst']['list'].append(
                    (u'{}{}'.format(a,
                                    u' ({})'.format(g) if g else u''), b))

        if len(errors['aucune_phrase_dst']['list']):
            errors['aucune_phrase_dst']['titles'].append(
                _("The following word have no sentence to go and therefore "
                  "can't be shown/used"))
            errors['aucune_phrase_dst']['titles'].append(
                    "&nbsp;&raquo; &raquo; {}".format(
                        _("You have to add a sentence that contains:")))
            result['errors'] = errors

        # pour debug :
        print(phrases_finales)
        # retour[u'phrases'] = phrases_finales
        return result
