from rest_framework import generics

from . import serializers

from risk_management.users import models
from rest_framework import viewsets


class UserlistView(generics.ListAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = 'uuid'


class UserCreateview(generics.CreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserCreationSerializer


class BusinessUnitview(generics.ListCreateAPIView):
    queryset = models.BusinessUnit.objects.all()
    serializer_class = serializers.BuSerializer
    lookup_field = 'uuid'
