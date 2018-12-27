from operator import itemgetter

from risk_register import models
from . import serializers

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.decorators import action


class RiskClassViewset(viewsets.GenericViewSet,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin):
    queryset = models.ClasseDeRisques.objects.all()
    serializer_class = serializers.RiskClassSerializer

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
            risk_serializer = serializers.RiskSerialiser(page, many=True,
                                                         fields=('code_risque', 'nom', 'definition', 'description',
                                                                 'cause', 'consequence', 'couverture', 'pilotage',
                                                                 'aide', 'note'))
            return self.get_paginated_response(risk_serializer.data)

        risk_serializer = serializers.RiskSerialiser(risks, many=True)
        return Response(risk_serializer.data)


class RiskViewSet(viewsets.GenericViewSet,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin):
    queryset = models.Risque.objects.all()
    serializer_class = serializers.RiskSerialiser

    @action(detail=True)
    def occurences(self, request, pk):
        pr = models.ProcessusRisque.objects.filter(risque__code_risque=pk)
        ar = models.ActiviteRisque.objects.filter(risque__code_risque=pk)
        p_s = serializers.ProcessRiskSerializer(pr, many=True)
        a_s = serializers.ActivityRiskSerializer(ar, many=True)
        data = sorted(p_s.data + a_s.data, key=itemgetter('created'), reverse=True)
        page = self.paginate_queryset(data)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(data)
