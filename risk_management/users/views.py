from itertools import chain
from dal import autocomplete
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.db.models import Q


from .models import User
from .forms import UserUpdateForm
from .utils import ecart_seuil_de_risque, followed_risks

logger = logging.getLogger(__name__)


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = 'employe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        pr = user.processusrisques_manages.all()
        ar = user.activiterisques_manages.all()
        # risques assignés à l'utilisateur trier par priorité croissant
        user_managed_risks = sorted(
            chain(pr, ar),
            key=ecart_seuil_de_risque,
            reverse=True
        )
        context['my_risks'] = user_managed_risks
        context['followed_risks'] = followed_risks(self.request.user)
        return context


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):

    form_class = UserUpdateForm

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"


class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return User.objects.none()

        qs = User.objects.all()

        if self.q:
            qs = qs.filter(Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q))
        return qs


class Userinfo(DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'users/user_info.html'
