import uuid
import logging
from datetime import timedelta

from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError, FieldError
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

from django_vox.models import VoxNotifications, VoxNotification
from django_vox.registry import channels
from django_vox.extra.background import BackgroundVoxModel as VoxModel

from model_utils.fields import StatusField, MonitorField
from model_utils import Choices
from model_utils.models import TimeFramedModel, TimeStampedModel

from risk_management.users.models import BusinessUnit

logger = logging.getLogger(__name__)


class RiskDataError(Exception):
    pass


class ProcessData(models.Model):
    nom = models.CharField(max_length=255)
    origine = models.ForeignKey('Processus', on_delete=models.SET_NULL,
                                null=True, blank=True, verbose_name=_('fournisseur interne'),
                                related_name='ouput_data',
                                help_text=_('Laisser vide si origine externe à l\'entreprise'))

    commentaire = models.CharField(max_length=255, blank=True, null=True,
                                   help_text=_('Veuillez indiquer le nom de l\'origine  externe ou laisser vide si'
                                               ' origine interne'),
                                   verbose_name=_('fournisseur externe'))

    def __str__(self):
        if self.origine:
            bu = self.origine.business_unit
            return '%s/%s/%s' % (bu, self.origine, self.nom)
        else:
            return '%s/%s' % (_('Origine externe'), self.nom)

    class Meta:
        ordering = ['nom']
        unique_together = (("nom", "origine"),)
        verbose_name = _('données du processus')
        verbose_name_plural = _('données des processus')


class Processus(VoxModel):
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
    proc_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name=_('manager du processus'),
                                     related_name='processus_manages')
    input_data = models.ManyToManyField('ProcessData', verbose_name=_('Données d\'entrée'),
                                        related_name='clients', blank=True
                                        )
    risques = models.ManyToManyField('Risque', through='ProcessusRisque')

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        if self.proc_manager:
            return reverse('risk_register:detail_processus', kwargs={'pk': self.code_processus})

    def get_bu_managers(self):
        if self.business_unit.bu_manager:
            yield self.business_unit.bu_manager
        else:
            return self.business_unit.get_risk_managers()

    def get_risk_managers(self):
        return self.business_unit.get_risk_managers()

    def get_proc_managers(self):
        yield self.proc_manager

    class Meta:
        verbose_name = _('processus')
        verbose_name_plural = _('processus')
        unique_together = (('business_unit', 'nom'),)

    class VoxMeta:
        notifications = VoxNotifications(
            create=VoxNotification(
                _('Notifier qu\'un nouveau processus a été créé'),
                actor_type='users.user', target_type='risk_register.processus'
            ),
            change_proc_manager=VoxNotification(
                _('Notifier que le manager du processus a changé'),
                actor_type='users.user', target_type='risk_register.processus'
            )
        )


class Activite(TimeFramedModel, VoxModel):
    STATUS = Choices(('pending', _('en cours')), ('completed', _('achevé')))
    code_activite = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=50, db_index=True,
                           verbose_name=_("Nom de l'activité"))
    description = models.CharField(max_length=500, blank=True, verbose_name=_('Description'))
    processus = models.ForeignKey(Processus, on_delete=models.CASCADE,
                                  verbose_name=_('Processus'), related_name='activites')
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    verbose_name=_('employé en charge'),
                                    related_name='activites')

    risques = models.ManyToManyField('Risque', through='ActiviteRisque')
    status = StatusField()
    acheve_le = MonitorField(monitor='status', when=['achevé'])

    class VoxMeta:
        notifications = VoxNotifications(
            create=VoxNotification(
                _('Notification qu\'une activité a été créée'),
                actor_type='users.user', target_type='risk_register.activite'
            ),
            complete=VoxNotification(
                _('Notification qu\'une activité a été achevée'),
                actor_type='users.user', target_type='risk_register.activite'
            ),
            delete=VoxNotification(
                _('Notification qu\'une activité a été supprimée'),
                actor_type='users.user', target_type='risk_register.activite'
            )
        )

    def __str__(self):
        return self.nom

    def clean(self):
        """s'assurer que la date de debut de l'activité précède la date de fin"""
        if (self.start and self.end) and (self.start > self.end):
            raise ValidationError(
                {
                    'end': _('l\'activité ne peut pas se terminer avant d\'avoir commencé!')
                })

    def get_absolute_url(self):
        return reverse('risk_register:detail_activite', kwargs={'pk': self.code_activite})

    def get_proc_manager(self):
        return self.processus.get_proc_managers()

    def get_responsable(self):
        yield self.responsable

    def get_risk_managers(self):
        return self.processus.get_risk_managers()

    class Meta:
        verbose_name = _('Activité')
        verbose_name_plural = _('activités')
        unique_together = (('nom', 'processus'),)
        ordering = ('nom',)


class ClasseDeRisques(models.Model):
    nom = models.CharField(_("Classe de risques"),
                           max_length=50, primary_key=True)

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('risk_register:liste_risques', kwargs={'classe': self.nom})

    class Meta:
        verbose_name = _('Classe de risques')
        verbose_name_plural = _('Classes de risques')


class Risque(TimeStampedModel, VoxModel):
    code_risque = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    classe = models.ForeignKey(ClasseDeRisques, on_delete=models.CASCADE, null=True)
    nom = models.CharField(max_length=200, verbose_name=_('nom'))
    description = models.TextField(max_length=500, db_index=True, verbose_name=_("description"))
    definition = models.CharField(max_length=200, blank=True, verbose_name=_('définition'))
    cause = models.TextField(max_length=500, verbose_name=_('cause(s)'))
    consequence = models.TextField(_("Conséquence(s)"), max_length=500)
    couverture = models.TextField(
        _("Actions / Couverture"), max_length=500, blank=True)
    pilotage = models.TextField(_("Pilotage / suivi"), max_length=500, blank=True)
    note = models.TextField(_("Réflexion à considérer à la lecture du risque"), max_length=255, blank=True)
    aide = models.TextField(_('Sommes-nous concernés'), max_length=255, blank=True)
    cree_par = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                 on_delete=models.SET_NULL, verbose_name=_('Crée par'))
    search_vector = SearchVectorField(null=True, blank=True)

    class VoxMeta:
        notifications = VoxNotifications(
            create=VoxNotification(
                _('Notification qu\'un nouveau risque a été créé'),
                actor_type='users.user', target_type='risk_register.risque'
            ),
        )

    def __str__(self):
        return '%s: %s...' % (self.nom, self.description[:50])

    def get_risk_managers(self):
        yield self.cree_par.__class__.objects.filter(is_superuser=True)

    class Meta:
        verbose_name = _('risque')
        verbose_name_plural = _('risques')
        ordering = ('created', 'nom', 'description')
        unique_together = (('nom', 'description'),)
        indexes = [GinIndex(fields=['search_vector'])]


class CritereDuRisque(models.Model):
    DETECTABILITE_CHOIX = (
        (1, 'Détection permanente'),
        (2, 'Détection élevée'),
        (3, 'Moyenne'),
        (4, 'Très basse'),
        (5, 'Capacité minime'),
        (6, 'Incapacité de détection'),
    )
    OCCURENCE_CHOIX = (
        (1, '1-Quasi impossible'),
        (2, '2-Très improbable'),
        (3, '3-Improbable'),
        (4, '4-Probable'),
        (5, '5-Très probable'),
        (6, '6-Quasi certain'),
    )
    SEVERITE_CHOIX = (
        (1, '1-Faible'),
        (2, '2-Moyenne'),
        (3, '3-Important'),
        (4, '4-Elevé'),
        (5, '5-Très elevé'),
        (6, '6-Maximal'),
    )
    detectabilite = models.SmallIntegerField(
        choices=DETECTABILITE_CHOIX, verbose_name=_('détectabilité'), default=3)
    occurence = models.SmallIntegerField(
        choices=OCCURENCE_CHOIX, default=3, verbose_name=_('ocurrence'))
    severite = models.SmallIntegerField(
        choices=SEVERITE_CHOIX, default=3, verbose_name=_('impact'))
    evalue_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True,
                                   verbose_name=_('évalué par'))

    def __str__(self):
        return 'D: %d; S: %d; O: %d' % (self.detectabilite, self.severite, self.occurence)

    def valeur_menace(self):
        """Renvoie le produit des score des critères"""
        return self.detectabilite * self.severite * self.occurence

    def valeur_opportunite(self):
        """si le risque est une opportunité, inverser la valeur de la détectabilité avant de calculer
         le produit des scores"""
        detectabilite_opp_choice = dict((x, y) for x, y in zip(range(1, 7), range(6, 0, -1)))
        detectabilite_opp = detectabilite_opp_choice.get(self.detectabilite)
        return detectabilite_opp * self.severite * self.occurence

    class Meta:
        verbose_name = _('critérisation')
        verbose_name_plural = _('critérisation')


class IdentificationRisque(TimeStampedModel):
    STATUS = Choices(('pending', _('en attente')), ('verified', _('confirmé')))
    TYPE_DE_RISQUE = (
        ('O', _('opportunité')),
        ('M', _('menace')),
    )
    code_identification = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    risque = models.ForeignKey(Risque, on_delete=models.CASCADE, verbose_name=_('risque'))
    type_de_risque = models.CharField(max_length=1, choices=TYPE_DE_RISQUE, default='M',
                                      verbose_name=_('type de risque'))
    date_revue = models.DateTimeField('revue', null=True, blank=True)
    criterisation = models.OneToOneField('CritereDuRisque', on_delete=models.SET_NULL, blank=True, null=True,
                                         verbose_name=_('Seuil de risque'))
    criterisation_change = MonitorField(monitor='criterisation')
    date_revue_change = MonitorField(monitor='date_revue')
    verifie = StatusField(verbose_name=_('vérification'))
    verifie_le = MonitorField(monitor='verifie')
    verifie_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        if self.date_revue and (self.date_revue < self.created):
            raise ValidationError(
                {'date_revue': _('la date de revue (%s) ne peut pas prédéder la date de cration (%s)' %
                                 (self.date_revue.date(), self.created.date()))}
            )
        super().clean()

    def save(self, *args, **kwargs):
        if self.verifie == 'verified' and not self.date_revue:
            # si le risque est verifié et la date de revue non fixé,
            # fixer la date de revue par défaut à un an dans le futur
            self.date_revue = now() + timedelta(days=365)
        super().save(*args, **kwargs)

    def seuil_de_risque(self):
        if self.est_obsolete:
            return
        elif self.criterisation:
            if self.type_de_risque == 'M':
                return self.criterisation.valeur_menace()
            elif self.type_de_risque == 'O':
                return self.criterisation.valeur_opportunite()

    seuil_de_risque.short_description = _('seuil de risque')

    def facteur_risque(self):
        if self.estimations.all():
            return self.estimations.latest().facteur_risque()

    facteur_risque.short_description = _('facteur risque')

    def seuil_display(self):
        """renvoie des classes css pour l'affichage html du seuil de risque"""
        seuil = self.seuil_de_risque()
        if seuil:
            return "text-info"
        return "text-muted"

    seuil_display.short_description = _('seuil de risque')

    def facteur_risque_display(self):
        """renvoi des classes css pour l'affichage html du facteur risque"""
        facteur_risque = self.facteur_risque()
        if facteur_risque:
            if self.seuil_de_risque():
                ratio = (self.facteur_risque() - self.seuil_de_risque()) / self.seuil_de_risque()
                if self.type_de_risque == 'M':
                    if ratio <= 0.1:
                        return "facteur-1"
                    elif 0.1 < ratio <= 0.3:
                        return "facteur-1-3"
                    elif 0.3 < ratio <= 0.5:
                        return "facteur-3-5"
                    elif ratio > 0.5:
                        return "facteur-5"
                elif self.type_de_risque == 'O':
                    if ratio <= 0.1:
                        return "facteur-5"
                    elif 0.1 < ratio <= 0.3:
                        return "facteur-3-5"
                    elif 0.3 < ratio <= 0.5:
                        return "facteur-1-3"
                    elif ratio > 0.5:
                        return "facteur-1"
            else:
                return "facteur-5"
        else:
            return "text-muted"

    def status(self):
        facteur_risque = self.facteur_risque()
        seuil = self.seuil_de_risque()
        if facteur_risque and seuil:
            if facteur_risque <= seuil:
                if self.type_de_risque == 'M':
                    return _('acceptable')
                elif self.type_de_risque == 'O':
                    return _('inacceptable')
            else:
                if self.type_de_risque == 'M':
                    return _('inacceptable')
                elif self.type_de_risque == 'O':
                    return _('acceptable')
        return 'inconnu'

    def status_display(self):
        """classe css pour l'affichage du statut du risque"""
        if self.status() == 'acceptable':
            return "text-success"
        elif self.status() == 'inacceptable':
            return "text-danger"
        else:
            return "text-muted"

    status.short_description = _('statut du risque')

    # le risque est-il assigné
    def est_assigne(self):
        return self.proprietaire is not None

    def get_class(self):
        return self.__class__.__name__

    @property
    def est_obsolete(self):
        if self.date_revue:
            return now() > self.date_revue
        return False

    class Meta:
        get_latest_by = 'created'
        abstract = True
        ordering = ('-created', 'verifie_le')


class ActiviteRisque(IdentificationRisque, VoxModel):
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE, verbose_name=_('activité'))
    soumis_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   related_name='activiterisques_soumis', null=True,
                                   verbose_name=_('soumis par'))
    modifie_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='activiterisques_modifies', verbose_name=_('modifié par'))
    suivi_par = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='activiterisques_suivis')
    proprietaire = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='activiterisques_manages', verbose_name=_('propriétaire du risque'))
    proprietaire_change = MonitorField(monitor='proprietaire')
    estimations = GenericRelation('Estimation', related_query_name='activiterisque')
    controles = GenericRelation('Controle', related_query_name='activiterisque')

    class VoxMeta:
        notifications = VoxNotifications(
            create=VoxNotification(
                _('Notification qu\'un nouveau risque a été identifié'),
                actor_type='users.user', target_type='risk_register.activiterisque'
            ),
            assign=VoxNotification(
                _('Notification que le risque a été assigné'),
                actor_type='users.user', target_type='risk_register.activiterisque'
            ),
            verify=VoxNotification(
                _('Notification que le risque est vérifié'),
                actor_type='users.user', target_type='risk_register.activiterisque'
            ),
            obsolete=VoxNotification(
                _('Notification que les données du risque sont obsolètes')
            )
        )

    def __str__(self):
        return "%s/%s (%s)" % (self.activite.nom, self.risque.nom, self.type_de_risque)

    # for django-vox channels
    def get_proprietaires(self):
        yield self.proprietaire

    def get_activity_owners(self):
        yield self.activite.responsable

    def get_proc_managers(self):
        yield self.activite.processus.proc_manager

    def get_bu_managers(self):
        return self.activite.processus.get_bu_managers()

    def get_risk_managers(self):
        return self.activite.processus.get_risk_managers()

    def get_suiveurs(self):
        return self.suivi_par.exclude(
            pk=self.soumis_par.pk).exclude(
            pk__in=self.get_proprietaires()).exclude(
            pk__in=self.get_proc_managers()).exclude(
            pk__in=self.get_bu_managers()).exclude(pk__in=self.get_risk_managers())

    def get_reporters(self):
        yield self.soumis_par

    class Meta(IdentificationRisque.Meta):
        verbose_name = _('risque de l\'activité')
        verbose_name_plural = _('risques des activités')
        unique_together = (('activite', 'risque', 'type_de_risque'),)


class ProcessusRisque(IdentificationRisque):
    processus = models.ForeignKey(Processus, on_delete=models.CASCADE, verbose_name=_('processus'))
    soumis_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   related_name='processusrisques_soumis', null=True,
                                   verbose_name=_('soumis par'))
    modifie_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='processusrisques_modifies', verbose_name=_('modifié par'))
    suivi_par = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='processusrisques_suivis')
    proprietaire = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='processusrisques_manages', verbose_name=_('propriétaire du risque'))
    proprietaire_change = MonitorField(monitor='proprietaire')
    estimations = GenericRelation('Estimation', related_query_name='processusrisque')
    controles = GenericRelation('Controle', related_query_name='processusrisque')

    class VoxMeta:
        notifications = VoxNotifications(
            create=VoxNotification(
                _('Notification qu\'un nouveau risque a été identifié'),
                actor_type='users.user', target_type='risk_register.processusrisque'
            ),
            assign=VoxNotification(
                _('Notification que le risque a été assigné'),
                actor_type='users.user', target_type='risk_register.processusrisque'
            ),
            verify=VoxNotification(
                _('Notification que le risque est vérifié'),
                actor_type='users.user', target_type='risk_register.processusrisque'
            ),
            obsolete=VoxNotification(
                _('Notification que les données du risque sont obsolètes')
            )
        )

    def __str__(self):
        return '%s/%s (%s)' % (self.processus.nom, self.risque.nom, self.type_de_risque)

    # for django-vox channels
    def get_proprietaires(self):
        yield self.proprietaire

    def get_proc_managers(self):
        yield self.processus.proc_manager

    def get_bu_managers(self):
        return self.processus.get_bu_managers()

    def get_risk_managers(self):
        return self.processus.get_risk_managers()

    def get_suiveurs(self):
        return self.suivi_par.exclude(
            pk=self.soumis_par.pk).exclude(
            pk__in=self.get_proprietaires()).exclude(
            pk__in=self.get_proc_managers()).exclude(
            pk__in=self.get_bu_managers()).exclude(pk__in=self.get_risk_managers())

    def get_reporters(self):
        yield self.soumis_par

    class Meta(IdentificationRisque.Meta):
        verbose_name = _('risque du processus')
        verbose_name_plural = _('risques des processus')
        unique_together = (('processus', 'risque', 'type_de_risque'),)


class RiskMixin(VoxModel):
    LIMIT = models.Q(app_label='risk_register',
                     model='activiterisque') | models.Q(app_label='risk_register',
                                                        model='processusrisque')
    content_type = models.ForeignKey(ContentType, limit_choices_to=LIMIT, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=36)
    content_object = GenericForeignKey()

    def get_bu_managers(self):
        return self.content_object.get_bu_managers()

    def get_risk_managers(self):
        return self.content_object.get_risk_managers()

    def get_proc_managers(self):
        return self.content_object.get_proc_managers()

    def get_risk_suiveurs(self):
        return self.content_object.get_suiveurs()

    def get_risk_reporters(self):
        return self.content_object.get_reporters()

    def get_risk_owner(self):
        return self.content_object.get_proprietaires()

    def get_act_responsable(self):
        if self.content_object.get_class() == 'ActiviteRisque':
            return self.content_object.activite.get_responsable()

    class Meta:
        abstract = True


class Estimation(TimeStampedModel, RiskMixin):
    code_estimation = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_revue = models.DateTimeField(_('Date de revue'), default=now)
    criterisation = models.OneToOneField(CritereDuRisque, on_delete=models.SET_NULL, blank=True, null=True,
                                         verbose_name=_('Scoring'))
    date_revue_change = MonitorField(monitor='date_revue')
    criterisation_change = MonitorField(monitor='criterisation')

    class VoxMeta:
        notifications = VoxNotifications(
            create=VoxNotification(
                _('Notification qu\'une estimation a été créée'),
                actor_type='users.user', target_type='risk_register.estimation'
            ),
            obsolete=VoxNotification(
                _('Notification qu\'une estimation est obsolete'),
            )
        )

    def get_estimators(self):
        yield self.criterisation.evalue_par

    def facteur_risque(self):
        """renvoit le facteur risque"""
        # si le risque est obsolète il n'y a pas de facteur risque
        if self.est_obsolete:
            return
        elif self.criterisation:
            if self.content_object.type_de_risque == 'M':
                return self.criterisation.valeur_menace()
            elif self.content_object.type_de_risque == 'O':
                return self.criterisation.valeur_opportunite()

    @property
    def est_obsolete(self):
        return now() > self.date_revue

    def save(self, *args, **kwargs):
        """s'assurer que les données du risque sont à jour et
        que la date de debut de l'activité précède la date de fin"""
        if self.content_object.est_obsolete:
            raise RiskDataError(
                _('Les donneés du risque ont besoins d\'une mise à jour'))
        if self.content_object.verifie == 'pending':
            logger.error("erreur lors de la sauvegarde d'une estimation")
            raise RiskDataError(
                _('On ne peut pas estimer un risque sans l\'avoir verifié')
            )
        super().save(*args, **kwargs)

    def clean(self):
        if self.created > self.date_revue:
            raise ValidationError(
                {'date_revue': _('La date de revue de l\'estimation ne peut pas précédée sa date de création')
                 })

    def __str__(self):
        return 'Estimation pour: %s' % self.content_object

    class Meta:
        verbose_name = _('Estimation du risque')
        verbose_name_plural = _('Estimations des risque')
        ordering = ('-created',)
        get_latest_by = "created"


class Controle(TimeFramedModel, TimeStampedModel, RiskMixin):
    STATUS = Choices(('in_progress', _('en cours')), ('completed', _('achevé')))
    code_traitement = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    critere_cible = models.CharField(max_length=1,
                                     choices={
                                         ('D', _('Détectabilité')), ('S', _('Sévérité')), ('O', _('Occurence'))},
                                     verbose_name=_('critère cible'), default='O')
    nom = models.CharField(max_length=50, verbose_name=_('intitulé'))
    description = models.CharField(max_length=500, verbose_name=_('détail'), null=True, blank=True)
    cree_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                 verbose_name=_('créé par'), null=True,
                                 related_name='traitements_crees')
    assigne_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name=_('assigné à'),
                                  null=True, related_name='traitements_assignes')
    modifie_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    related_name='traitements_modifies',
                                    null=True, blank=True, verbose_name=_('modifié par'))
    # ajouté a la liste des contrôles à mettre en eouvre
    est_approuve = models.BooleanField(verbose_name=_('approuvé'), default=False)
    # validé l'exécution du contrôle
    est_valide = models.BooleanField(verbose_name=_('validé'), default=False)
    status = StatusField()
    acheve_le = MonitorField(monitor='status', when=['completed'])

    class VoxMeta:
        notifications = VoxNotifications(
            create=VoxNotification(
                _('Notification qu\'un contrôle a été ajouté'),
                actor_type='users.user', target_type='risk_register.controle'
            ),
            approve=VoxNotification(
                _('Notification que le contrôle a été approuvé')
                ,
                actor_type='users.user', target_type='risk_register.controle'
            ),
            complete=VoxNotification(
                _('Notification qu\'un controle a été implementé'),
                actor_type='users.user', target_type='risk_register.controle'
            ),
            validate=VoxNotification(
                _('Notification qu\'un contrôle a été validé'),
                actor_type='users.user', target_type='risk_register.controle'
            ),
            assign=VoxNotification(
                _('Notification que le contrôle est assigné'),
                actor_type='users.user', target_type='risk_register.controle'
            )
        )

    def get_creator(self):
        yield self.cree_par

    def get_proprietaire(self):
        return self.assigne_a

    def clean(self):
        if (self.start and self.end) and (self.start > self.end):
            raise ValidationError(
                {'end': _('la date de fin ne peut pas précédée celle du début. Veuillez corriger le champ "debut".')}
            )

    def save(self, *args, **kwargs):
        if (self.start and self.end) and (self.start > self.end):
            logger.error("erreur de sauvergarde du controle '%s'" % self.nom)
            raise FieldError(
                'la date de fin ne peut pas précédée celle du début. Veuillez corriger le champ "debut".'
            )
        if self.content_object and not self.content_object.estimations.all():
            logger.error("erreur de sauvergarde du controle '%s'" % self.nom)
            raise RiskDataError(
                {self.content_type.name: _(' le risque n\'a pas encore été estimé')}
            )
        elif self.content_object and (self.content_object.est_obsolete or
                                      self.content_object.estimations.latest().est_obsolete):
            logger.error("erreur de sauvergarde du controle '%s'" % self.nom)
            raise RiskDataError(
                _('Les donneés du risque ont besoins d\'une mise à jour'))
        super().save(*args, **kwargs)

    def est_en_retard(self):
        if self.end and (self.status == 'in_progress' and self.end < now()):
            return True
        return False

    def status_display(self):
        if self.est_en_retard():
            return 'text-danger h5'
        return 'text-muted'

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = _('contrôle')
        verbose_name_plural = _('contrôles')
        ordering = ('start',)
        get_latest_by = 'created'


# ---------- django-vox channels ----------
#  processus
channels[Processus].add('bu_manager', _('Manager du Business unit'), get_user_model(),
                        Processus.get_proc_managers)
channels[Processus].add('risk_manager', _('Manager du risque'), get_user_model(), Processus.get_risk_managers)

# risques
channels[Risque].add('risk_manager', _('Manager du risque'), get_user_model(), Risque.get_risk_managers)

# activites
channels[Activite].add('risk_manager', _('Manager du risque'), get_user_model(), Activite.get_risk_managers)
channels[Activite].add('activity_owner', _('Responsable de l\'activité'), get_user_model(), Activite.get_responsable)
channels[Activite].add('activity_manager', _('Manager de l\'activité'), get_user_model(), Activite.get_proc_manager)

# activiterisques

channels[ActiviteRisque].add('activity_owner', _('Responsable de l\'activité'), ActiviteRisque.get_activity_owners)
channels[ActiviteRisque].add('proc_manager', _('Manager du processus'), ActiviteRisque.get_proc_managers)
channels[ActiviteRisque].add('risk_manager', _('Manager du risque'), ActiviteRisque.get_risk_managers)
channels[ActiviteRisque].add('risk_reporter', _('la personne qui a soumis le risque'), ActiviteRisque.get_reporters)
channels[ActiviteRisque].add('risk_followers', _('Ceux qui suivent le risque'), ActiviteRisque.get_suiveurs)
channels[ActiviteRisque].add('risk_owner', _('Propriétaire du risque'), ActiviteRisque.get_proprietaires)

# processusrisques

channels[ProcessusRisque].add('proc_manager', _('Manager du processus'), ProcessusRisque.get_proc_managers)
channels[ProcessusRisque].add('bu_manager', _('Manager du Business unit'), ProcessusRisque.get_bu_managers)
channels[ProcessusRisque].add('risk_manager', _('Manager du risque'), ProcessusRisque.get_risk_managers)
channels[ProcessusRisque].add('risk_reporter', _('La personne qui a soumis le risque'), ProcessusRisque.get_reporters)
channels[ProcessusRisque].add('risk_owner', _('Propriétaire du risque'), ProcessusRisque.get_proprietaires)
channels[ProcessusRisque].add('risk_followers', _('Ceux qui suivent le risque'), ProcessusRisque.get_suiveurs)

# estimations

channels[Estimation].add('risk_manager', _('Manager du risque'), Estimation.get_risk_managers)
channels[Estimation].add('risk_owner', _('Propriétaire du risque'), Estimation.get_risk_owner)
channels[Estimation].add('risk_followers', _('Ceux qui suivent le risque'), Estimation.get_risk_suiveurs)
channels[Estimation].add('bu_manager', _('Manager du Business Unit'), Estimation.get_bu_managers)
channels[Estimation].add('proc_manager', _('Manager du Processus'), Estimation.get_proc_managers)
channels[Estimation].add('activity_owner', _('Responsable de l\'activité'), Estimation.get_act_responsable)
channels[Estimation].add('estimator', _('l\'estimateur du risque'), Estimation.get_estimators)

# contrôles

channels[Controle].add('risk_manager', _('Manager du risque'), Controle.get_risk_managers)
channels[Controle].add('risk_owner', _('Propriétaire du risque'), Controle.get_risk_owner)
channels[Controle].add('proc_manager', _('Manager du processus'), Controle.get_proc_managers)
channels[Controle].add('control_creator', _('Créateur du contrôle'), Controle.get_creator)
channels[Controle].add('control_owner', _('Propriétaire du controle'), Controle.get_proprietaire)

