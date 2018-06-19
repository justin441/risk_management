from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.translation import ugettext_lazy as _

# Register your models here.
from .models import (Processus, ProcessData, Activite, Risque, ClasseDeRisques, ActiviteRisque, Estimation,
                     Controle, ProcessusRisque, CritereDuRisque)


class DonneesSortieProcessusInline(admin.StackedInline):
    extra = 1
    model = ProcessData
    verbose_name = _('donnée de sortie')
    verbose_name_plural = _('données de sortie')
    classes = ['collapse']


class DonneesEntreeProcessusInline(admin.StackedInline):
    extra = 1
    model = Processus.input_data.through
    verbose_name = 'Donnée d\'entrée'
    verbose_name_plural = "Données d'entrée"
    classes = ['collapse']
    autocomplete_fields = ['processdata_id']


@admin.register(Processus)
class ProcessAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['type_processus', 'business_unit', 'nom', 'description', 'proc_manager']})
    ]
    search_fields = ['nom']
    inlines = [
        DonneesEntreeProcessusInline,
        DonneesSortieProcessusInline
    ]
    autocomplete_fields = ['proc_manager']


@admin.register(Activite)
class ActiviteAdmin(admin.ModelAdmin):
    search_fields = ['nom']
    autocomplete_fields = [
        'responsable',
        'processus'
    ]


@admin.register(ClasseDeRisques)
class ClasseAdmin(admin.ModelAdmin):
    pass


@admin.register(Risque)
class RisqueAdmin(admin.ModelAdmin):
    search_fields = ['description']


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
    inlines = [
        EstimationInline,
        ControleInline,
    ]


@admin.register(CritereDuRisque)
class CriterdurisqueAdmin(admin.ModelAdmin):
    pass


@admin.register(ActiviteRisque)
class ActiviteRisqueAdmin(IdentificationRisque):
    fields = ['activite', 'type_de_risque', 'risque', 'criterisation', 'verifie']
    autocomplete_fields = ['activite', 'risque']


@admin.register(ProcessusRisque)
class ProcessusRisqueAdmin(IdentificationRisque):
    fields = ['processus', 'type_de_risque', 'risque', 'criterisation', 'verifie']
    autocomplete_fields = ['processus', 'risque']


@admin.register(ProcessData)
class ProcessDataAdmin(admin.ModelAdmin):
    autocomplete_fields = ['origine']
    search_fields = ['nom']
