from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.conf import settings

import logging
from uuid import uuid4

from django_vox.models import VoxNotifications, VoxNotification
from django_vox.extra.background import BackgroundVoxModel as VoxModel
from django_vox.registry import channels
from django_vox.base import Contact

phone_regex = RegexValidator(regex=r'^(\(\+\d{0,3}\))? ?\d{9}$',
                             message=_("le format du numéro de téléphone est:[(+000)][ ]000000000;"
                                       "les parties entre crochet sont optionnelles. "
                                       "exemple: (+237) 674228621, 674228621, (+234)674228621"))

logger = logging.getLogger('django')


class BusinessUnit(VoxModel):
    """Représente un business unit au sens large, soit une société soit un projet"""

    denomination = models.CharField(max_length=100, primary_key=True, verbose_name=_('Nom'),
                                    help_text=_("Nom de la société ou du projet; doit être unique."))
    uuid = models.UUIDField(db_index=True, default=uuid4, editable=False)
    raison_sociale = models.CharField(max_length=50, verbose_name=_('raison sociale'), blank=True, null=True)
    sigle = models.CharField(max_length=10, blank=True, help_text=_('exemple: C.T.C'))
    marche = models.CharField(_("objet"), max_length=200, blank=True, help_text=_('activités de l\'entrepriser'
                                                                                  ' / but du projet'))
    ville_siege = models.CharField(_("ville"), max_length=25)
    adresse_physique = models.CharField(max_length=200, help_text=_("Rue, quartier, lieu-dit"))
    adresse_postale = models.CharField(max_length=32, blank=True, verbose_name=_("Adresse postale"))
    telephone = models.CharField(max_length=18, default='(+237) 000000000', validators=[phone_regex],
                                 help_text=_("L'indicatif est optionnel. exemple: (+237) 694484246"),
                                 verbose_name=_('Numero de Téléphone'))
    bu_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='bu_manages',
                                   null=True, blank=True, verbose_name=_('manager'))
    employes = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Position', related_name='business_units')
    site_web = models.URLField(verbose_name=_('site internet'), null=True, blank=True)
    projet = models.BooleanField(default=False, help_text=_('Le Business Unit est-il un Projet?'))

    class VoxMeta:
        notifications = VoxNotifications(
            create=VoxNotification(
                _('Notifier aux administrateurs qu\'un nouveau business unit a été créé'),
                actor_type='users.user', target_type='users.businessunit'
            ),
            delete=VoxNotification(
                _('Notifier aux administrateurs qu\'un business unit a été supprimé'),
                actor_type='users.user', target_type='users.businessunit'
            )
        )

    def __str__(self):
        return self.denomination

    @property
    def id(self):
        # necessaire pour utiliser le paramètre target de Vox notification
        return self.pk

    def get_absolute_url(self):
        return reverse('risk_register:detail_business_unit', kwargs={'pk': self.pk})

    def get_managers(self):
        if self.bu_manager:
            yield self.bu_manager
        else:
            return User.objects.filter(is_superuser=True)

    def get_risk_managers(self):
        return User.objects.filter(is_superuser=True)

    class Meta:
        verbose_name_plural = "Business Units"
        ordering = ('denomination',)

    def get_bu_type(self):
        if self.projet:
            return _('projet')
        else:
            return 'business unit'


class User(AbstractUser):
    """Représente un utilisateur du système"""
    MADAME = 'Mme'
    MONSIEUR = 'M.'
    DOCTEUR = 'Dr'
    PROFESSEUR = 'Pr'

    CIVILITE_CHOIX = (
        (MADAME, _('Madame')),
        (MONSIEUR, _('Monsieur')),
        (DOCTEUR, _('Docteur')),
        (PROFESSEUR, _('Professeur')),
    )
    uuid = models.UUIDField(db_index=True, default=uuid4, editable=False)
    civilite = models.CharField(
        max_length=3, choices=CIVILITE_CHOIX, default=MONSIEUR, verbose_name=_("titre"))
    first_name = models.CharField(_('prénom'), max_length=30)
    last_name = models.CharField(_('nom'), max_length=150)
    email = models.EmailField(max_length=255, unique=True)
    telephone = models.CharField(max_length=18, validators=[phone_regex],
                                 help_text=_("numero de téléphone à 9 chiffres, l'indicatif est optionnel"))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('civilite', 'firs_name', "last_name")

    def __str__(self):
        return '%s %s' % (self.civilite, self.get_full_name())

    def get_username(self):
        return self.username[:-36]

    def get_contacts_for_notification(self, _notification):
        yield Contact(self.get_full_name(), 'email', self.email)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    class Meta:
        ordering = ('first_name', 'last_name')


class Position(VoxModel):
    """Représente un poste de travail au sein d'un business unit"""
    poste = models.CharField(max_length=30, verbose_name=_('poste'))
    employe = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Employé(e)'),
                                related_name=_('postes'))
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)

    class VoxMeta:
        notifications = VoxNotifications(
            create=VoxNotification(
                _('Notification qu\'un poste a été créé'),
                actor_type='users.user'
            )
        )

    def get_holders(self):
        yield self.employe

    class Meta:
        ordering = ('poste',)
        unique_together = (('employe', 'business_unit', 'poste'),)

    def __str__(self):
        return self.poste

# -------- django_vox channels --------


channels[BusinessUnit].add('risk_manager', _('Manager du risque'), User, BusinessUnit.get_risk_managers)
channels[BusinessUnit].add('bu_manager', _('Manager du Business unit'), User, BusinessUnit.get_managers)
channels[Position].add('position_holder', _('Titulaire du poste'), User, Position.get_holders)
