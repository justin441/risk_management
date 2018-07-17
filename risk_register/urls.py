from django.urls import path

from . import views

app_name = 'risk_register'

urlpatterns = [
    path('business-unit/<str:pk>/', views.BusinessUnitRiskRegisterView.as_view(), name='detail_business_unit'),
    path('process/<uuid:pk>/', views.ProcessusRiskRegisterView.as_view(), name='detail_processus'),
    path('activity/<uuid:pk>/', views.ActiviteRiskRegisterView.as_view(), name='detail_activite'),
    path('<str:business_unit>/create-process/', views.CreateProcessView.as_view(), name='creer_processus'),
    path('<uuid:pk>/update-process/', views.UpdateProcessView.as_view(), name='modifier_processus'),
    path('<uuid:processus>/update-input-list/', views.AddProcessInputView.as_view(), name='ajout_entree'),
    path('<uuid:pk>/delete-process/', views.DeleteProcessView.as_view(), name='effacer_processus'),
    path('<uuid:processus>/add-activity/', views.CreateActiviteView.as_view(), name='creer_activite'),
    path('<uuid:pk>/update-activity/', views.UpdateActiviteView.as_view(), name='modifier_activite'),
    path('<uuid:pk>/delete-activity/', views.DeleteActiviteView.as_view(), name='effacer_activite'),
    path('<uuid:processus>/add-output/', views.CreateProcessOutputView.as_view(), name='ajout_sortie'),
    path('<uuid:processus>/add-risk-to-process/', views.AddProcessusrisqueView.as_view(), name='ajout_processusrisque'),
    path('<uuid:processus>/create-process-risk/', views.NewRiskForProcessView.as_view(), name='creer_risque_processus'),
    path('<uuid:processusrisque>/edit-process-risk/', views.EditProcessusrisqueView.as_view(),
         name='modifier_processusrisque'),
    path('<uuid:processusrisque>/delete-process-risk/', views.DeleteProcessusrisqueView.as_view(),
         name='effacer_processusrisque'),
    path('<uuid:activite>/add-risk-to-activity/', views.AddActiviterisqueView.as_view(), name='ajout_activiterisque'),
    path('<uuid:activite>/create-activity-risk/', views.NewRiskForActivityView.as_view(), name='creer_risque_activite'),
    path('risk-detail/<uuid:pk>/', views.RiskDetailView.as_view(), name='detail_risque'),
    path('<uuid:activiterisque>/edit-activity-risk/', views.EditActiviterisqueView.as_view(),
         name='modifier_activiterisque'),
    path('<uuid:activiterisque>/delete-activity-risk/', views.DeleteActiviterisqueView.as_view(),
         name='effacer_activiterisque'),
    path('risque-autocomplete/', views.RiskAutocomplete.as_view(), name='risque-autocomplete')
]
