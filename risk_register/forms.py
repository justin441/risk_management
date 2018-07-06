from django import forms

from .models import Processus


class CreateProcessForm(forms.ModelForm):
    class Meta:
        model = Processus
        exclude = ['input_data']

