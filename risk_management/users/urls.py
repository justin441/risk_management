from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path("", view=views.UserListView.as_view(), name="list"),
    path("~redirect/", view=views.UserRedirectView.as_view(), name="redirect"),
    path("~update/", view=views.UserUpdateView.as_view(), name="update"),
    path(
        "<str:username>",
        view=views.UserDetailView.as_view(),
        name="detail",
    ),
    path('user-autocomplete/', views.UserAutocomplete.as_view(), name='user-autocomplete'),
    path('user-info/<int:pk>/', views.Userinfo.as_view(), name='user_info')
]
