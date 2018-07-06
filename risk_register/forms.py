from django import forms

from .models import Processus


class CreateProcessForm(forms.ModelForm):
    class Meta:
        model = Processus
        exclude = ['business_unit', 'input_data']




