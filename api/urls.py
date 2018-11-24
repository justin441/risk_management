from django.urls import include, path

from api.users import api_views


urlpatterns = [
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration', include('rest_auth.registration.urls')),
    path('users/', api_views.UserlistView.as_view()),
    path('business-units/', api_views.BusinessUnitview.as_view())


]
