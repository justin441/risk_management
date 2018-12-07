from risk_register import models
from . import serializers

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response


class RiskClassViewset(viewsets.ModelViewSet):

    queryset = models.ClasseDeRisques.objects.all()
    serializer_class = serializers.RiskClassSerialiser

    @action(detail=True)
    def risks(self, request, pk=None):
        classe = self.get_object()
        risks = models.Risque.objects.filter(classe=classe.pk)
        page = self.paginate_queryset(risks)
        if page is not None:
            risk_serializer = serializers.RiskSerialiser(page, many=True)
            return self.get_paginated_response(risk_serializer.data)

        risk_serializer = serializers.RiskSerialiser(risks, many=True)
        return Response(risk_serializer.data)
