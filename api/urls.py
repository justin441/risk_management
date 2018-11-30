from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.users import api_views as users_api_view
from api.risk_register import api_views as risk_register_api_view
from rest_framework.schemas import get_schema_view

schema_view = get_schema_view(title='Risk API')

router = DefaultRouter()
router.register(r'users', users_api_view.UserlistView)
router.register(r'businessunits', users_api_view.BusinessUnitviewSet)
router.register(r'positions', users_api_view.PositionViewSet)
router.register(r'risk_classes', risk_register_api_view.RiskClassViewset)

urlpatterns = [
    path('rest-auth/logout/', users_api_view.RmLogoutView.as_view(), name='rest_logout'),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration', include('rest_auth.registration.urls')),
    path('schema/', schema_view),
    path('', include(router.urls))
]
