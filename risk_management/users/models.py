from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.conf import settings

phone_regex = RegexValidator(regex=r'^(\(\+\d{0,3}\))? ?\d{9}$',
                             message=_("le format du numéro de téléphone est:[(+000)][ ]000000000;"
                                       "les parties entre crochet sont optionnelles. "
                                       "exemple: (+237) 674228621, 674228621, (+234)674228621"))


class BusinessUnit(models.Model):
    """Représente un business unit au sens large, soit une société soit un projet"""

    denomination = models.CharField(max_length=100, primary_key=True, verbose_name=_('Dénomination'),
                                    help_text=_("Nom de la société ou du projet"))
    sigle = models.CharField(max_length=10, blank=True, help_text=_('exemple: C.T.C'))
    marche = models.CharField(_("Domaine d'activité"), max_length=200, blank=True)
    ville_siege = models.CharField(_("ville siège"), max_length=25)
    adresse_physique = models.CharField(max_length=200, help_text=_("Rue, quartier, lieu-dit"))
    adresse_postale = models.CharField(max_length=32, blank=True, verbose_name=_("Adresse postale"))
    telephone = models.CharField(max_length=18, default='(+237) 000000000', validators=[phone_regex],
                                 help_text=_("L'indicatif est optionnel. exemple: (+237) 694484246"),
                                 verbose_name=_('Numero de Téléphone'))
    bu_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='bu_manages',
                                   null=True, blank=True, verbose_name=_('manager'))
    employes = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Position', related_name='business_unit')
    site_web = models.URLField(verbose_name=_('site internet'), null=True, blank=True)
    projet = models.BooleanField(default=False, help_text=_('Le Business Unit est-il un Projet?'))

    def __str__(self):
        return self.denomination

    def get_absolute_url(self):
        return reverse('risk_register:detail_business_unit', kwargs={'pk': self.denomination})

    class Meta:
        verbose_name_plural = "Business Units"
        ordering = ('denomination', )


class User(AbstractUser):
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

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    class Meta:
        ordering = ('first_name', 'last_name')


class Position(models.Model):
    poste = models.CharField(max_length=30, verbose_name=_('poste'))
    employe = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Employé(e)'),
                                related_name=_('postes'))
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)

    class Meta:
        ordering = ('poste',)
        unique_together = (('employe', 'business_unit'),)

    def __str__(self):
        return self.poste
