from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Processus, ProcessData


@receiver(m2m_changed, sender=Processus.input_data.through)
def change_input_data(sender, **kwargs):
    action = kwargs['action']
    instance = kwargs['instance']

    if isinstance(instance, Processus) and kwargs['model'] == ProcessData:
        if action == 'pre_add':
            for data in kwargs['pk_set'].copy():
                if (ProcessData.objects.get(pk=data).origine == instance) \
                   or (not ProcessData.objects.get(pk=data).origine.business_unit == instance.business_unit):
                    kwargs['pk_set'].remove(data)
