
from django import forms

from .models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'civilite', 'first_name', 'last_name',
                  'business_unit', 'fonction', 'telephone']

    def signup(self, request, user):
        pass







