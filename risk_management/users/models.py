from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from django.utils.functional import cached_property


phone_regex = RegexValidator(regex=r'^(\(\+\d{0,3}\))? ?\d{9}$',
                             message=_("le format du numéro de téléphone est:[(+000) ]999999999;"
                                       "la partie entre crochet est optionnel. "
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
    projet = models.BooleanField(default=False, help_text=_('Le Business Unit est-il un Projet?'))

    def __str__(self):
        return self.denomination

    @property
    def bu_manager(self):
        if self.projet:
            try:
                bu_manager = self.employes.get(fonction__iexact='Chef de projet')
            except User.DoesNotExist:
                return _("Non defini")
            return bu_manager
        else:
            try:
                bu_manager = self.employes.get(fonction__iexact='Directeur général')
            except User.DoesNotExist:
                return _("Non defini")
            return bu_manager

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
        max_length=3, choices=CIVILITE_CHOIX, default=MONSIEUR, verbose_name=_("Titre"))
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=150)
    business_unit = models.ForeignKey('BusinessUnit', on_delete=models.CASCADE, related_name='employes',
                                      verbose_name=_("Business Unit"))
    fonction = models.CharField(max_length=100, verbose_name=_('poste'), help_text=_('exemple: Directeur général'))
    email = models.EmailField(max_length=255, unique=True)
    telephone = models.CharField(max_length=18, validators=[phone_regex],
                                 help_text=_("numero de téléphone à 9 chiffres, l'indicatif est optionnel"))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('civilite', 'firs_name', "last_name")

    def __str__(self):
        return self.get_full_name()

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def make_manager(self):
        if self.business_unit.projet:
            self.fonction = 'Chef de projet'
        else:
            self.fonction = 'Directeur Général'


