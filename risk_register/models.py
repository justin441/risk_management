import uuid
from datetime import timedelta

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.utils.html import format_html
from django.conf import settings

from model_utils.fields import StatusField, MonitorField
from model_utils import Choices
from model_utils.models import TimeFramedModel, TimeStampedModel

from risk_management.users.models import BusinessUnit


class DonneesDeRisqueObsolete(Exception):
    pass


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
    proc_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name=_('manager du processus'),
                                     related_name='processus_manages')
    input_data = models.ManyToManyField('ProcessData', verbose_name=_('Données d\'entrée'),
                                        related_name='clients'
                                        )

    def __str__(self):
        return "%s: %s" % (self.business_unit.denomination, self.nom)

    # def get_absolute_url(self):
    #     if self.proc_manager:
    #         return reverse('risk_register:manager_home', kwargs={'username': self.proc_manager})

    class Meta:
        verbose_name_plural = 'processus'
        unique_together = (('business_unit', 'nom'), )


class ProcessData(models.Model):

    nom = models.CharField(max_length=255)
    origine = models.ForeignKey(Processus, on_delete=models.SET_NULL,
                                null=True, blank=True, verbose_name=_('Origine'),
                                related_name='ouput_data',
                                help_text=_('Laisser vide si origine externe à l\'entreprise'))

    commentaire = models.CharField(max_length=255, blank=True,
                                   help_text=_('Veuillez indiquer le nom de l\'origine  externe'),
                                   verbose_name=_('commentaires'))

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']
        unique_together = (("nom", "origine"),)
        verbose_name = 'données du processus'
        verbose_name_plural = 'données des processus'


class Activite(TimeFramedModel):
    STATUS = Choices(('pendind', _('en cours')), ('completed', _('achevé')))
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

    def __str__(self):
        return self.nom

    def clean(self):
        """s'assurer que la date de debut de l'activité précède la date de fin"""
        if self.start > self.end:
            raise ValidationError(
                {
                    'end': _('l\'activité ne peut pas se terminer avant d\'avoir commencé!')
                })

    # def get_absolute_url(self):
    #     return reverse('risk_register:detail_activite', kwargs={'pk': self.code_activite})

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

    # def get_absolute_url(self):
    #     return reverse('risk_register:liste_risque', kwargs={'nom': self.nom})

    class Meta:
        verbose_name = _('Classe de risques')
        verbose_name_plural = _('Classes de risques')


class Risque(models.Model):
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

    def __str__(self):
        return self.description

    class Meta:
        ordering = ('description',)
        unique_together = (('nom', 'description'),)


class CritereDuRisque(models.Model):
    DETECTABILITE_CHOIX = (
        (1, '1-Détection permanente'),
        (2, '2-Détection élevée'),
        (3, '3-Moyenne'),
        (4, '4-Très basse'),
        (5, '5-Capacité minime'),
        (6, '6-Incapacité de détection'),
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
        (3, '3-Sérieux'),
        (4, '4-Grave'),
        (5, '5-Très Grave'),
        (6, '6-Catastrophique'),
    )
    detectabilite = models.SmallIntegerField(
        choices=DETECTABILITE_CHOIX, verbose_name=_('détectabilité'), default=3)
    occurence = models.SmallIntegerField(
        choices=OCCURENCE_CHOIX, default=3, verbose_name=_('ocurrence'))
    severite = models.SmallIntegerField(
        choices=SEVERITE_CHOIX, default=3, verbose_name=_('sévérité'))
    evalue_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True,
                                   verbose_name=_('évalué par'))

    def __str__(self):
        return 'D: %d; S: %d; O: %d' % (self.detectabilite, self.severite, self.occurence)

    def valeur(self):
        """Renvoie le produit des score des critères"""
        return self.detectabilite * self.severite * self.occurence

    class Meta:
        verbose_name = _('Critérisation')


class IdentificationRisque(TimeStampedModel):
    STATUS = Choices((0, 'pending', _('en attente')), (1, 'verified', _('confirmé')))
    TYPE_DE_RISQUE = (
        ('O', _('opportunité')),
        ('M', _('menace')),
    )
    code_identification = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    risque = models.ForeignKey(Risque, on_delete=models.CASCADE, verbose_name=_('risque'))
    type_de_risque = models.CharField(max_length=1, choices=TYPE_DE_RISQUE, default='M',
                                      verbose_name=_('type de risque'))
    date_revue = models.DateTimeField(
        'revue prévue pour le: ', default=now() + timedelta(days=365))
    criterisation = models.OneToOneField('CritereDuRisque', on_delete=models.SET_NULL, blank=True, null=True,
                                         verbose_name=_('Seuil de risque'))
    criterisation_change = MonitorField(monitor='criterisation')
    date_revue_change = MonitorField(monitor='date_revue')
    verifie = StatusField(verbose_name=_('vérification'))
    verifie_le = MonitorField(monitor='verifie')
    verifie_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        if self.date_revue < self.created:
            raise ValidationError(
                {
                    'date_revue': 'La date de revue du revue du risque ( %s ) ne peut pas précédée la date \
                    de son identification ( %s )' % (
                        self.date_revue, self.created)})
        if self.modified and (self.modified < self.created):
            raise ValidationError(
                {
                    'modified': 'La date de modification du risque ( %s ) ne peut pas précédée la date \
                    de son identification ( %s )' % (
                        self.modified, self.created)}
            )

    def seuil_de_risque(self):
        if self.criterisation:
            return self.criterisation.valeur()

    def facteur_risque(self):
        if self.estimations.all():
            return self.estimations.latest().facteur_risque()

    def seuil_diplay(self):
        """Affichage html du seuil de risque"""
        seuil = self.seuil_de_risque()
        if seuil:
            return format_html(
                '<span style="color:#007bff" class="seuil-defini">{}</span>',
                seuil
            )
        else:
            return format_html(
                '<span style="color:#dc143c" class="seuil-indefini">{}</span>',
                seuil
            )

    def facteur_risque_display(self):
        """Affichage html du facteur risque"""
        facteur_risque = self.facteur_risque()
        if facteur_risque:
            if self.seuil_de_risque():
                ratio = (self.facteur_risque() - self.seuil_de_risque()) / self.seuil_de_risque()
                if ratio <= 0.1:
                    return format_html(
                        '<span style="color: #003300" class="facteur-defini">{}</span>',
                        facteur_risque
                    )
                elif 0.1 < ratio <= 0.3:
                    return format_html(
                        '<span style="color: #483e19" class="facteur-defini">{}</span>',
                        facteur_risque
                    )
                elif 0.3 < ratio <= 0.5:
                    return format_html(
                        '<span style="color: #bb3b12" class="facteur-defini">{}</span>',
                        facteur_risque
                    )
                elif ratio > 0.5:
                    return format_html(
                        '<span style="color: #dc2434" class="facteur-defini">{}</span>',
                        facteur_risque
                    )
            else:
                return format_html(
                    '<span style="color: #dc143c" class="facteur-defini">{}</span>',
                    facteur_risque
                )
        else:
            return format_html(
                '<span style="color: #dc143c" class="facteur-indefini">{}</span>',
                'Le risque n\'est pas encore estimé.'
            )

    def status(self):
        if self.seuil_de_risque() and self.facteur_risque():
            if self.facteur_risque() <= self.seuil_de_risque():
                return _('acceptable')
            else:
                return _('inacceptable')

    # le risque est-il assigné
    def est_assigne(self):
        if self.estimations.all() and self.estimations.latest().proprietaire:
            return True
        return False

    def get_proprietaire(self):
        if self.est_assigne():
            return self.estimations.latest().proprietaire

    @property
    def est_obsolete(self):
        return now() > self.date_revue

    class Meta:

        get_latest_by = 'created'
        abstract = True


class ActiviteRisque(IdentificationRisque):
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE, verbose_name=_('activité'))
    soumis_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   related_name='activiterisques_soumis', null=True,
                                   verbose_name=_('soumis par'))
    modifie_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='activiterisques_modifies', verbose_name=_('modifié par'))
    estimations = GenericRelation('Estimation', related_query_name='activiterisque')
    controles = GenericRelation('Controle', related_query_name='activiterisque')

    def __str__(self):
        return "%s/%s" % (self.activite.nom, self.risque.nom)

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
    estimations = GenericRelation('Estimation', related_query_name='processusrisque')
    controles = GenericRelation('Controle', related_query_name='processusrisque')

    def __str__(self):
        return '%s/%s' % (self.processus.nom, self.risque.nom)

    class Meta(IdentificationRisque.Meta):
        verbose_name = _('risque du processus')
        verbose_name_plural = _('risques des processus')
        unique_together = (('processus', 'risque', 'type_de_risque'),)
        ordering = ('created', 'processus')


class RiskMixin(models.Model):
    LIMIT = models.Q(app_label='risk_register',
                     model='activiterisque') | models.Q(app_label='risk_register',
                                                        model='processusrisque')
    content_type = models.ForeignKey(ContentType, limit_choices_to=LIMIT, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=36)
    content_object = GenericForeignKey()

    class Meta:
        abstract = True


class Estimation(TimeStampedModel, RiskMixin):
    code_estimation = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_revue = models.DateTimeField(_('revue prevue pour le'), default=now()+timedelta(days=60))
    criterisation = models.OneToOneField(CritereDuRisque, on_delete=models.SET_NULL, blank=True, null=True,
                                         verbose_name=_('Scoring'))
    proprietaire = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='risques_manages', verbose_name=_('propriétaire du risque'))
    date_revue_change = MonitorField(monitor='date_revue')
    criterisation_change = MonitorField(monitor='criterisation')
    proprietaire_change = MonitorField(monitor='proprietaire')

    def facteur_risque(self):
        """renvoit le facteur risque"""
        if self.criterisation:
            return self.criterisation.valeur()

    @property
    def est_obsolete(self):
        return now() > self.date_revue

    def save(self, *args, **kwargs):
        """s'assurer que les données du risque sont à jour et
        que la date de debut de l'activité précède la date de fin"""
        if self.content_object.est_obsolete:
            raise DonneesDeRisqueObsolete(
                'Les donneés du risque ont besoins d\'une mise à jour')
        super().save(*args, **kwargs)

    def clean(self):
        if self.created > self.date_revue:
            raise ValidationError(
                {'date_revue': 'La date de revue de l\'estimation ne peut pas précédée sa date de création'
                 })

    def __str__(self):
        return 'Estimation pour: %s' % self.content_object

    class Meta:
        verbose_name = _('Estimation du risque')
        verbose_name_plural = _('Estimations des risque')
        ordering = ('-created',)
        get_latest_by = "created"


class Controle(TimeFramedModel, TimeStampedModel, RiskMixin):
    STATUS = Choices((0, 'in_progress', _('en cours')), (1, 'completed', _('achevé')))
    code_traitement = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    critere_cible = models.CharField(max_length=1,
                                     choices={
                                         ('D', _('Détectabilité')), ('S', _('Sévérité')), ('O', _('Occurence'))},
                                     verbose_name=_('critère cible'), default='O')
    nom = models.CharField(max_length=300, verbose_name=_('nom'))
    cree_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                 verbose_name=_('créé par'), null=True,
                                 related_name='traitements_crees')
    assigne_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name=_('assigné à'),
                                  null=True, related_name='traitement_assignes')
    modifie_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    related_name='traitements_modifies',
                                    null=True, blank=True, verbose_name=_('modifié par'))
    status = StatusField()
    acheve_le = MonitorField(monitor='status', when=['achevé'])

    def clean(self):
        if self.start > self.end:
            raise ValidationError(
                {'end': _('la date de fin ne peut pas précédée celle du début. Veuillez corriger le champ "debut".')}
            )

    def save(self, *args, **kwargs):
        # todo inclure les exceptions présent ici dans les vues
        if self.content_object.est_obsolete or (
            self.content_object.estimations.all() and self.content_object.estimations.latest().est_obsolete
        ):
            raise DonneesDeRisqueObsolete(
                'Les donneés du risque ont besoins d\'une mise à jour')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = 'Contrôle'
        verbose_name_plural = 'Contrôles'
        ordering = ('start',)
        get_latest_by = 'created'
