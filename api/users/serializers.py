from rest_framework import serializers
from risk_management.users.models import User, BusinessUnit, Position
from risk_register.models import Processus


from allauth.account.adapter import get_adapter
from allauth.utils import email_address_exists
from allauth.account import app_settings as allauth_settings
from allauth.account.utils import setup_user_email

from django.utils.translation import ugettext as _


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('business_unit', 'employe', 'poste')


class UserSerializer(serializers.ModelSerializer):
    postes = PositionSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = ('pk', 'uuid', 'email', 'civilite', 'first_name', 'last_name', 'get_username', 'telephone', 'postes')
        depth = 1
        extra_kwargs = {
            'email': {'write_only': True},
        }


class UserCreationSerializer(serializers.ModelSerializer):
    # adapté de rest_auth.registration.serializers.RegistrationSerializer

    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'civilite', 'first_name', 'last_name', 'telephone')
        extra_kwargs = {
            'email': {'required': allauth_settings.EMAIL_REQUIRED}
        }

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("Un utilisateur est déjà enregistré avec cet email."))
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("Les deux mots de passe entrés sont differents."))
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
            'civilite': self.validated_data.get('civilite', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'telephone': self.validated_data.get('telephone', '')
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class ProcessusDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Processus
        fields = ('code_processus', 'nom', 'description')


class BuSerializer(serializers.ModelSerializer):
    processus_set = ProcessusDetailSerializer(many=True)

    class Meta:
        model = BusinessUnit
        fields = ('uuid', 'denomination', 'raison_sociale', 'sigle', 'marche', 'ville_siege', 'adresse_physique',
                  'projet', 'adresse_postale', 'telephone', 'site_web', 'bu_manager', 'employes', 'processus_set')
