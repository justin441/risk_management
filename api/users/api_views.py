from operator import itemgetter

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import authentication
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response

from rest_auth.views import LogoutView

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from . import serializers
from api.risk_register.serializers import ActivityDetailSerializer, ActivityRiskSerialiser, ProcessRiskSerialiser

from risk_management.users import models
from risk_register.models import Processus, Activite, ProcessusRisque, ActiviteRisque


@api_view()
@permission_classes([permissions.IsAuthenticated])
def get_user_id(request):
    return Response(
        data={'id': request.user.uuid,
              'firstName': request.user.first_name,
              'lastName': request.user.last_name},
        headers={'Cache-Control': 'no-cache'}
    )


class UserlistView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    """
    Lister les utilisateurs.
    """
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = 'uuid'


class UserCreateview(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
    Creer un utilisateur
    """
    queryset = models.User.objects.all()
    serializer_class = serializers.UserCreationSerializer


class BusinessUnitviewSet(viewsets.ModelViewSet):
    """
        Lister, creer, modifier, detailler et supprimer les business unit
    """
    queryset = models.BusinessUnit.objects.all()
    serializer_class = serializers.BuSerializer
    lookup_field = 'uuid'

    @action(detail=True)
    def processes(self, request, uuid=None):
        bu = self.get_object()
        processes = Processus.objects.filter(business_unit=bu.pk)
        page = self.paginate_queryset(processes)
        if page is not None:
            process_serializer = serializers.ProcessusDetailSerializer(page, many=True)
            return self.get_paginated_response(process_serializer.data)

        process_serializer = serializers.ProcessusDetailSerializer(processes, many=True)
        return Response(process_serializer.data)

    @action(detail=True)
    def activities(self, request, uuid=None):
        bu = self.get_object()
        activities = Activite.objects.filter(processus__business_unit=bu.pk)
        page = self.paginate_queryset(activities)
        if page is not None:
            activity_serializer = ActivityDetailSerializer(page, many=True)
            return self.get_paginated_response(activity_serializer.data)

        activity_serializer = ActivityDetailSerializer(activities, many=True)
        return Response(activity_serializer.data)

    @action(detail=True)
    def risks(self, request, uuid=None):
        bu = self.get_object()
        pr = ProcessusRisque.objects.filter(processus__business_unit=bu)
        ar = ActiviteRisque.objects.filter(activite__processus__business_unit=bu)
        p_s = ProcessRiskSerialiser(pr, many=True)
        a_s = ActivityRiskSerialiser(ar, many=True)
        data = sorted(p_s.data+a_s.data, key=itemgetter('created'), reverse=True)
        page = self.paginate_queryset(data)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(data)


class PositionViewSet(viewsets.ModelViewSet):
    """
    Lister, creer, modifier, detailler et supprimer les postes
    """
    queryset = models.Position.objects.all()
    serializer_class = serializers.PositionSerializer


class RmLogoutView(LogoutView):
    authentication_classes = (authentication.TokenAuthentication,)



