from django.urls import path

from . import views

app_name = 'risk_register'

urlpatterns = [
    path('<str:denomination>/', views.BusinessUnitDetailView.as_view(), name='detail_business_unit'),
]
