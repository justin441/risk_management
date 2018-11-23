from rest_framework import serializers
from risk_management.users.models import User, BusinessUnit, Position


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'civilite', 'first_name', 'last_name', 'telephone')


class BuSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessUnit
        fields = ('denomination', 'raison_sociale', 'sigle', 'marche', 'ville_siege', 'adresse_physique', 'projet',
                  'adresse_postale', 'telephone', 'site_web', 'bu_manager', 'employes', )


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('business_unit', 'employe', 'poste')
