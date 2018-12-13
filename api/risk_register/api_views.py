from risk_register import models
from . import serializers

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response


class RiskClassViewset(viewsets.GenericViewSet,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin):

    queryset = models.ClasseDeRisques.objects.all()
    serializer_class = serializers.RiskClassSerialiser

    @property
    def paginator(self):
        if self.action == 'list':
            return None
        return super().paginator

    def retrieve(self, request, *args, **kwargs):
        """List the risks of a risk class"""
        classe = self.get_object()
        risks = models.Risque.objects.filter(classe=classe.pk)
        page = self.paginate_queryset(risks)
        if page is not None:
            risk_serializer = serializers.RiskSerialiser(page, many=True, fields=('nom', 'description', 'cause',
                                                                                  'consequence'))
            return self.get_paginated_response(risk_serializer.data)

        risk_serializer = serializers.RiskSerialiser(risks, many=True)
        return Response(risk_serializer.data)
