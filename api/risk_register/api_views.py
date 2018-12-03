from risk_register import models
from . import serializers

from rest_framework import viewsets
from rest_framework import mixins


class RiskClassViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    This viewset provides provides only 'list' action.
    """
    queryset = models.ClasseDeRisques.objects.all()
    serializer_class = serializers.RiskClassSerialiser


class RiskViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    pass


