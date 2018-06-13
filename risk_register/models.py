import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from risk_management.users.models import User, BusinessUnit


class Processus(models.Model):
    PROCESSUS_MANAGEMENT = 'PM'
    PROCESSUS_OPERATIONNEL = 'PO'
    PROCESSUS_SOUTIEN = 'PS'
    TYPE_PROCESSUS_CHOICES = (
        (PROCESSUS_MANAGEMENT, _('Processus de management')),
        (PROCESSUS_OPERATIONNEL, _('Processus opérationnel')),
        (PROCESSUS_SOUTIEN, _('Processus de soutien'))
    )
    code_processus = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    type_processus = models.CharField(max_length=2, choices=TYPE_PROCESSUS_CHOICES, default='PO',
                                      verbose_name=_('Type de Processus'))
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, verbose_name=_('Propriétaire'))
    nom = models.CharField(max_length=50, db_index=True, verbose_name=_('Nom'))
    description = models.CharField(max_length=300)
    proc_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('manager du processus'),
                                     related_name='processus_manages')

    def __str__(self):
        return self.nom

    # def get_absolute_url(self):
    #     if self.proc_manager:
    #         return reverse('risk_register:manager_home', kwargs={'username': self.proc_manager})

    class Meta:
        verbose_name_plural = 'processus'
        # permissions = (
        #     ('ajouter_activite', 'peut_ajouter des activités du processus'),
        #     ('supprimer_activite', 'peut supprimer des activités du processus'))


class DonneesProcessus(models.Model):
    """Ce a pour rôle d'enregistrer les données d'entrées et de sortie d'un processus"""

    nom = models.CharField(max_length=255)
    processus1 = models.ForeignKey(Processus, on_delete=models.SET_NULL,
                                   null=True, blank=True, verbose_name=_('Origine'),
                                   related_name='ouput_data',
                                   help_text=_('Laisser vide si origine externe à l\'entreprise'))
    processus2 = models.ForeignKey(Processus, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name=_('Destination'), related_name='input_data',
                                   help_text=_('Laisser vide si destination externe à l\'entreprise'))

    @property
    def fournisseur(self):
        if self.processus1:
            return self.processus1
        else:
            return 'Fournisseur externe'

    @property
    def client(self):
        if self.processus2:
            return self.processus2
        else:
            return 'Client externe'

    def clean(self):
        if (not self.processus1) and (not self.processus2):
            raise ValidationError(
                {'Process': _('Au moins un des champs Origine et Destination doit comporter une valeur')}
            )

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']
        unique_together = (('nom', 'processus1',), ('nom', 'processus2'),)


