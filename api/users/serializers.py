from rest_framework import serializers
from risk_management.users.models import User, BusinessUnit, Position


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = []


class BuSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessUnit
        fields = []


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = []
