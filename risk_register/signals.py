from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from .models import Processus, ProcessData


@receiver(m2m_changed, sender=Processus.input_data.through)
def change_input_data(sender, **kwargs):
    """Après avoir modifier la liste des données d'entrée du processus , vérifier si elle ne contient pas
    une ou plusieurs données sorties du même processus et supprimer celles-ci ."""
    action = kwargs['action']
    instance = kwargs['instance']

    if isinstance(instance, Processus) and kwargs['model'] == ProcessData:
        if action == 'pre_add':
            for data in kwargs['pk_set'].copy():
                if (ProcessData.objects.get(pk=data).origine == instance) \
                   or (not ProcessData.objects.get(pk=data).origine.business_unit == instance.business_unit):
                    kwargs['pk_set'].remove(data)

