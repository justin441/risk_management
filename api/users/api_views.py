from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import authentication
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from rest_auth.views import LogoutView

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from . import serializers

from risk_management.users import models


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


class PositionViewSet(viewsets.ModelViewSet):
    """
    Lister, creer, modifier, detailler et supprimer les postes
    """
    queryset = models.Position.objects.all()
    serializer_class = serializers.PositionSerializer


class RmLogoutView(LogoutView):
    authentication_classes = (authentication.TokenAuthentication,)



