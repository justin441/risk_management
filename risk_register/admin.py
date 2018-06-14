from django.contrib import admin

# Register your models here.
from .models import Processus, DonneesProcessus


@admin.register(DonneesProcessus)
class DonneesProcessusAdmin(admin.ModelAdmin):
    pass


@admin.register(Processus)
class ProcessAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['type_processus', 'business_unit', 'nom', 'descritption', 'proc_manager']})
    ]
