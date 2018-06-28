from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.translation import gettext_lazy as _

from risk_management.users.admin import risk_management_admin_site

# Register your models here.
from .helpers import get_changes_between_2_objects
from .models import (Processus, ProcessData, Activite, Risque, ClasseDeRisques, ActiviteRisque, Estimation,
                     Controle, ProcessusRisque, CritereDuRisque)


class DonneesSortieProcessusInline(admin.StackedInline):
    extra = 1
    model = ProcessData
    verbose_name = _('donnée de sortie')
    verbose_name_plural = _('données de sortie')
    classes = ['collapse']


@admin.register(Processus, site=risk_management_admin_site)
class ProcessAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['type_processus', 'business_unit', 'nom', 'description', 'proc_manager', 'input_data']})
    ]
    search_fields = ['nom']
    inlines = [
        DonneesSortieProcessusInline
    ]
    autocomplete_fields = ['proc_manager', 'business_unit']
    filter_horizontal = ['input_data']
    list_display = ['__str__', 'type_processus', 'business_unit', 'description', 'proc_manager']
    list_filter = ('type_processus', 'business_unit', 'business_unit__projet')


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

    mark_completed.short_description = _('marquer comme achevé')


@admin.register(ClasseDeRisques, site=risk_management_admin_site)
class ClasseAdmin(admin.ModelAdmin):
    pass


@admin.register(Risque, site=risk_management_admin_site)
class RisqueAdmin(admin.ModelAdmin):
    exclude = ['cree_par']
    search_fields = ['description']
    list_display = ['nom', 'description', 'cause', 'consequence', 'couverture', 'pilotage']
    list_filter = ('classe',)
    list_editable = ['couverture', 'pilotage']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.cree_par = request.user
        super().save_model(request, obj, form, change)


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


class ControleInline(GenericStackedInline):
    model = Controle
    extra = 1
    classes = ['collapse']
    exclude = ['acheve_le', 'cree_par', 'modifie_par']


class IdentificationRisque(admin.ModelAdmin):
    exclude = ['criterisation_change', 'date_revue_change', 'verifie_le', 'verifie_par']
    inlines = [
        EstimationInline,
        ControleInline,
    ]
    date_hierarchy = 'created'
    list_editable = ['verifie', 'date_revue']
    actions = ['mark_verified']

    def mark_verified(self, request, queryset):
        queryset = queryset.filter(verifie=0)
        queryset.update(verifie=1)
        queryset.update(verifie_par=request.user)

    mark_verified.short_description = _('marquer comme verifier')

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, Controle):
                try:
                    curr = Controle.objects.get(pk=obj.pk)
                except Controle.DoesNotExist:
                    obj.cree_par = request.user
                else:
                    if get_changes_between_2_objects(obj, curr, exclude=ControleInline.exclude):
                        obj.modifie_par = request.user
        formset.save()

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
        super().save_model(request, obj, form, changes)


@admin.register(CritereDuRisque, site=risk_management_admin_site)
class CriterdurisqueAdmin(admin.ModelAdmin):
    exclude = ['evalue_par']
    list_display = ['detectabilite', 'severite', 'occurence', 'valeur']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.evalue_par = request.user
        super().save_model(request, obj, form, change)


@admin.register(ActiviteRisque, site=risk_management_admin_site)
class ActiviteRisqueAdmin(IdentificationRisque):
    fields = ['activite', 'type_de_risque', 'risque', 'criterisation', 'verifie']
    autocomplete_fields = ['activite', 'risque']

    list_filter = ('activite__processus__business_unit', 'type_de_risque')
    list_display = ['created', 'date_revue', 'activite', 'risque', 'type_de_risque', 'verifie',
                    'status', 'seuil_diplay', 'facteur_risque_display', 'get_proprietaire']


@admin.register(ProcessusRisque, site=risk_management_admin_site)
class ProcessusRisqueAdmin(IdentificationRisque):
    fields = ['processus', 'type_de_risque', 'risque', 'criterisation', 'verifie']
    autocomplete_fields = ['processus', 'risque']
    list_filter = ('processus__business_unit', 'type_de_risque')
    list_display = ['created', 'date_revue', 'processus', 'risque', 'type_de_risque', 'verifie',
                    'status',  'seuil_diplay', 'facteur_risque_display', 'get_proprietaire']


@admin.register(ProcessData, site=risk_management_admin_site)
class ProcessDataAdmin(admin.ModelAdmin):
    autocomplete_fields = ['origine']
    search_fields = ['nom']
    list_display = ['nom', 'origine', 'commentaire']
    list_editable = ['commentaire']
