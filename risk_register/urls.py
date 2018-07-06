from django.urls import path

from . import views

app_name = 'risk_register'

urlpatterns = [
    path('<str:pk>/', views.BusinessUnitRiskRegisterView.as_view(), name='detail_business_unit'),
    path('process/<uuid:pk>/', views.ProcessusRiskRegisterView.as_view(), name='detail_processus'),
    path('activity/<uuid:pk>/', views.ActiviteRiskRegisterView.as_view(), name='detail_activite'),
    path('<str:business_unit>/create-process/', views.CreateProcessView.as_view(), name='creer_processus'),
]
