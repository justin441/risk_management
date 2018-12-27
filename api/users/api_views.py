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
from api.risk_register.serializers import ActivitySerializer, ProcessSerializer, ActivityRiskSerializer,\
    ProcessRiskSerializer

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
    list users
    """
    queryset = models.User.objects.all()
    serializer_class = serializers.UserDetailSerializer
    lookup_field = 'uuid'


class UserCreateview(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
        User registration
    """
    queryset = models.User.objects.all()
    serializer_class = serializers.UserCreationSerializer


class BusinessUnitviewSet(viewsets.ModelViewSet):
    """
        list, create, udpdate, retrieve and delete Business units
    """
    queryset = models.BusinessUnit.objects.all()
    serializer_class = serializers.BuSerializer
    lookup_field = 'uuid'

    @property
    def paginator(self):
        if self.action == "list":
            return None
        return super().paginator

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        if self.action == 'list':
            kwargs['fields'] = ('uuid', 'denomination', 'projet')
            return serializer_class(*args, **kwargs)
        return serializer_class(*args, **kwargs)

    @action(detail=True)
    def processes(self, request, uuid=None):
        """
        list the processes of a business unit
        :param request:
        :param uuid:
        :return:
        """
        bu = self.get_object()
        processes = Processus.objects.filter(business_unit=bu.pk)
        page = self.paginate_queryset(processes)
        if page is not None:
            process_serializer = ProcessSerializer(page, many=True, fields=('code_processus', 'type_processus', 'nom',
                                                                            'description'))
            return self.get_paginated_response(process_serializer.data)

        process_serializer = ProcessSerializer(processes, many=True, fields=('code_processus','type_processus', 'nom',
                                                                             'description'))
        return Response(process_serializer.data)

    @action(detail=True)
    def activities(self, request, uuid=None):
        """
        lists all the activities in all the processes of a business unit
        :param request:
        :param uuid:
        :return:
        """
        bu = self.get_object()
        activities = Activite.objects.filter(processus__business_unit=bu.pk)
        page = self.paginate_queryset(activities)
        if page is not None:
            activity_serializer = ActivitySerializer(page, many=True, fields=('code_activite', 'nom', 'description',
                                                                              'status'))
            return self.get_paginated_response(activity_serializer.data)

        activity_serializer = ActivitySerializer(activities, many=True, fields=('code_activite', 'nom', 'description',
                                                                                'status'))
        return Response(activity_serializer.data)

    @action(detail=True)
    def risks(self, request, uuid=None):
        """
        list all the risks identified in a business unit
        :param request:
        :param uuid:
        :return:
        """
        bu = self.get_object()
        pr = ProcessusRisque.objects.filter(processus__business_unit=bu)
        ar = ActiviteRisque.objects.filter(activite__processus__business_unit=bu)
        p_s = ProcessRiskSerializer(pr, many=True)
        a_s = ActivityRiskSerializer(ar, many=True)
        data = sorted(p_s.data+a_s.data, key=itemgetter('created'), reverse=True)
        page = self.paginate_queryset(data)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(data)


class PositionViewSet(viewsets.ModelViewSet):
    """
    create, retrieve, update, list and delete positions
    """
    queryset = models.Position.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.PositionDetailSerializer
        else:
            return serializers.PositionCreationSerializer


class RmLogoutView(LogoutView):
    """Log out user"""
    authentication_classes = (authentication.TokenAuthentication,)


