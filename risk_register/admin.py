import logging

from django.contrib import admin
from django.db.models import Q

from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.translation import gettext_lazy as _
from risk_management.users.admin import risk_management_admin_site
from risk_management.users.utils import get_changes_between_2_objects, get_latests

from .models import (Processus, ProcessData, Activite, Risque, ClasseDeRisques, ActiviteRisque, Estimation,
                     Controle, ProcessusRisque, CritereDuRisque)
from .forms import ProcessAdminForm
from risk_management.users.models import User


# todo: inclure rules
class DonneesSortieProcessusInline(admin.StackedInline):
    extra = 1
    model = ProcessData
    exclude = ['commentaire']
    verbose_name = _('donnée de sortie')
    verbose_name_plural = _('données de sortie')
    classes = ['collapse']


@admin.register(Processus, site=risk_management_admin_site)
class ProcessAdmin(admin.ModelAdmin):
    form = ProcessAdminForm
    fieldsets = [
        (None, {'fields': ['type_processus', 'business_unit', 'nom', 'description', 'proc_manager', 'input_data']})
    ]
    search_fields = ['nom']
    inlines = [
        DonneesSortieProcessusInline
    ]
    autocomplete_fields = ['business_unit']
    filter_horizontal = ['input_data']
    list_display = ['__str__', 'type_processus', 'business_unit', 'description', 'proc_manager']
    list_filter = ('type_processus', 'business_unit', 'business_unit__projet')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'proc_manager':
            if 'change' in request.get_full_path():
                qs = Processus.objects.get(pk=request.get_full_path().split('/')[4]).business_unit.employes.all()
                kwargs['queryset'] = qs
            else:
                kwargs['queryset'] = User.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'input_data':
            if 'change' in request.get_full_path():
                proc = Processus.objects.get(pk=request.get_full_path().split('/')[4])
                qs = ProcessData.objects.filter(
                    Q(origine__business_unit=proc.business_unit) | Q(origine__business_unit=None)).exclude(
                    origine=proc
                )
                kwargs['queryset'] = qs
            else:
                kwargs['queryset'] = ProcessData.objects.none()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        old = False
        if change:
            old = True
        super().save_model(request, obj, form, change)

        if old:
            current = obj.__class__.objects.get(pk=obj.pk)
            if 'proc_manager' in get_changes_between_2_objects(current, obj):
                logging.getLogger('django').info("Le manager du processus '{}' a été changé.".format(obj.nom))
                obj.issue_notification('change_proc_manager', actor=request.user, target=obj)
                logging.getLogger('django').info('Notification sent')

        else:
            logging.getLogger('django').info('New process added to {}'.format(obj.business_unit))
            obj.issue_notification('create', actor=request.user, target=obj)
            logging.getLogger('django').info('Notification sent.')


@admin.register(Activite, site=risk_management_admin_site)
class ActiviteAdmin(admin.ModelAdmin):
    exclude = ['acheve_le']
    search_fields = ['nom']
    autocomplete_fields = [
        'responsable',
        'processus'
    ]
    list_display = ['nom', 'description', 'processus', 'responsable', 'start', 'end', 'status']
    list_filter = ('processus__business_unit', 'status', 'processus__business_unit__projet')
    date_hierarchy = 'start'
    list_editable = ['start', 'end']
    actions = ['mark_completed']

    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
        logging.getLogger('django.request').info(
            "%s a achevé %d activité(s): %s" % (
                request.user.get_full_name(), len(queryset),
                ', '.join([activite['nom'] for activite in queryset.values('nom')])))

    mark_completed.short_description = _('marquer comme achevé')

    def save_model(self, request, obj, form, change):
        old = False
        if change:
            old = True
        super().save_model(request, obj, form, change)
        if old:
            current = Activite.objects.get(pk=obj.pk)
            if obj.responsable and 'responsable' in get_changes_between_2_objects(current, obj):
                obj.issue_notification('assign', actor=request.user, target=obj)
            if 'status' in get_changes_between_2_objects(current, obj):
                if obj.status == 'completed':
                    obj.issue_notification('complete', actor=request.user, target=obj)
                else:
                    obj.issue_notification('create_proc_mgr', actor=request.user, target=obj)
                    obj.issue_notification('assign', actor=request.user, target=obj)
        else:
            obj.issue_notification('create_proc_mgr', actor=request.user, target=obj)
            obj.issue_notification('assign', actor=request.user, target=obj)

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        obj.issue_notification('delete', actor=request.user, target=obj)


@admin.register(ClasseDeRisques, site=risk_management_admin_site)
class ClasseAdmin(admin.ModelAdmin):
    pass


@admin.register(Risque, site=risk_management_admin_site)
class RisqueAdmin(admin.ModelAdmin):
    exclude = ['cree_par', 'search_vector']
    search_fields = ['description']
    list_display = ['nom', 'description', 'cause', 'consequence']
    list_filter = ('classe',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.cree_par = request.user
        super().save_model(request, obj, form, change)
        obj.issue_notification('create', actor=request.user, target=obj)


class EstimationInline(GenericStackedInline):
    model = Estimation
    extra = 1
    classes = ['collapse']
    exclude = [
        'date_revue_change',
        'criterisation_change',
        'proprietaire_change'
    ]
    verbose_name = 'estimation du risque'
    verbose_name_plural = 'estimations du risque'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return get_latests(qs, 2)


class ControleInline(GenericStackedInline):
    model = Controle
    extra = 1
    classes = ['collapse']
    exclude = ['acheve_le', 'cree_par', 'modifie_par']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(status='completed')


class IdentificationRisque(admin.ModelAdmin):
    exclude = ['criterisation_change', 'date_revue_change', 'verifie_le', 'verifie_par']
    inlines = [
        EstimationInline,
        ControleInline,
    ]
    date_hierarchy = 'created'
    actions = ['mark_verified']
    list_display_links = ['risque']
    radio_fields = {'verifie': admin.HORIZONTAL}

    def mark_verified(self, request, queryset):
        queryset = queryset.filter(verifie='pending')
        liste_risques = [str(ident.code_identification) + ": " + ident.risque.description[:25]
                         + '...' for ident in queryset]
        queryset.update(verifie='verified')
        queryset.update(verifie_par=request.user)

        logging.getLogger('django.request').info('%s a vérifié %d risque(s): %s' % (request.user.get_full_name(),
                                                                                    len(queryset),
                                                                                    ', '.join(liste_risques)))
        logging.getLogger('django').info('%s a vérifié %d risque(s): %s' % (request.user.get_full_name(),
                                                                            len(queryset),
                                                                            ', '.join(liste_risques)))

    mark_verified.short_description = _('marquer comme verifier')

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, Controle):
                try:
                    curr = Controle.objects.get(pk=obj.pk)
                except Controle.DoesNotExist:
                    obj.cree_par = request.user
                    obj.save()
                    obj.issue_notification('create', actor=request.user, target=obj)
                else:
                    if get_changes_between_2_objects(obj, curr, exclude=ControleInline.exclude):
                        obj.modifie_par = request.user
                        obj.save()
                        if obj.assigne_a and 'assigne_a' in get_changes_between_2_objects(curr, obj):
                            obj.issue_notification('assign', target=obj, actor=request.user)
                        if 'est_approuve' in get_changes_between_2_objects(curr, obj):
                            obj.issue_notification('approve', target=obj, actor=request.user)
                        if obj.est_valide and 'est_valide' in get_changes_between_2_objects(curr, obj):
                            obj.issue_notification('validate', target=obj, actor=request.user)
                        if 'status' in get_changes_between_2_objects(curr, obj):
                            if obj.status == 'completed':
                                obj.issue_notification('complete', target=obj, actor=request.user)
                            else:
                                if obj.assigne_a:
                                    obj.issue_notification('assign', target=obj, actor=request.user)

            if isinstance(obj, Estimation):
                try:
                    curr = Estimation.objects.get(pk=obj.pk)
                except Estimation.DoesNotExist:
                    obj.save()
                    obj.issue_notification('create', actor=request.user, target=obj)
                else:
                    obj.save()

    def save_model(self, request, obj, form, change):
        if change:
            curr = obj.__class__.objects.get(pk=obj.pk)
            changes = get_changes_between_2_objects(obj, curr, exclude=self.exclude)
            if changes:
                obj.modifie_par = request.user
                if 'verifie' in changes:
                    if obj.verifie:
                        obj.verifie_par = request.user
                    else:
                        obj.verifie_par = None
        else:
            obj.soumis_par = request.user
        super().save_model(request, obj, form, change)


@admin.register(CritereDuRisque, site=risk_management_admin_site)
class CriterdurisqueAdmin(admin.ModelAdmin):
    exclude = ['evalue_par']
    list_display = ['detectabilite', 'severite', 'occurence']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.evalue_par = request.user
        super().save_model(request, obj, form, change)


@admin.register(ActiviteRisque, site=risk_management_admin_site)
class ActiviteRisqueAdmin(IdentificationRisque):
    fields = ['activite', 'type_de_risque', 'risque', 'criterisation', 'verifie', 'proprietaire', 'date_revue']
    autocomplete_fields = ['activite', 'risque']

    list_filter = ('activite__processus__business_unit', 'type_de_risque')
    list_display = ['created', 'date_revue', 'activite', 'risque', 'type_de_risque', 'verifie',
                    'verifie_par', 'status', 'seuil_de_risque', 'facteur_risque', 'proprietaire']

    def save_model(self, request, obj, form, change):
        old = False
        if change:
            old = True
        super().save_model(request, obj, form, change)
        if old:
            current = ActiviteRisque.objects.get(pk=obj.pk)
            if 'type_de_risque' in get_changes_between_2_objects(current, obj):
                obj.issue_notification('set_risk_type', actor=request.user, target=obj)
            if 'criterisation' in get_changes_between_2_objects(current, obj):
                obj.issue_notification('set_seuil', actor=request.user, target=obj)
            if obj.verifie == 'verified' and 'verifie' in get_changes_between_2_objects(current, obj):
                obj.issue_notification('verify', actor=request.user, target=obj)
            if obj.proprietaire and 'proprietaire' in get_changes_between_2_objects(current, obj):
                obj.issue_notification('assign', actor=request.user, target=obj)


@admin.register(ProcessusRisque, site=risk_management_admin_site)
class ProcessusRisqueAdmin(IdentificationRisque):
    fields = ['processus', 'type_de_risque', 'risque', 'criterisation', 'verifie', 'proprietaire', 'date_revue']
    autocomplete_fields = ['processus', 'risque']
    list_filter = ('processus__business_unit', 'type_de_risque')
    list_display = ['created', 'date_revue', 'processus', 'risque', 'type_de_risque', 'verifie',
                    'verifie_par', 'status', 'seuil_de_risque', 'facteur_risque', 'proprietaire']

    def save_model(self, request, obj, form, change):
        old = False
        if change:
            old = True
        super().save_model(request, obj, form, change)
        if old:
            current = ProcessusRisque.objects.get(pk=obj.pk)
            if 'type_de_risque' in get_changes_between_2_objects(current, obj):
                obj.issue_notification('set_risk_type', actor=request.user, target=obj)
            if 'criterisation' in get_changes_between_2_objects(current, obj):
                obj.issue_notification('set_seuil', actor=request.user, target=obj)
            if obj.verifie == 'verified' and 'verifie' in get_changes_between_2_objects(current, obj):
                obj.issue_notification('verify', actor=request.user, target=obj)
            if obj.proprietaire and 'proprietaire' in get_changes_between_2_objects(current, obj):
                obj.issue_notification('assign', actor=request.user, target=obj)


@admin.register(ProcessData, site=risk_management_admin_site)
class ProcessDataAdmin(admin.ModelAdmin):
    autocomplete_fields = ['origine']
    search_fields = ['nom']
    list_display = ['nom', 'origine', 'commentaire']
    list_editable = ['commentaire']
