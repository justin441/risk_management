from dal import autocomplete

from django import forms

from .models import Processus


class CreateProcessForm(forms.ModelForm):
    class Meta:
        model = Processus
        exclude = ['business_unit', 'input_data']
        widgets = {
            'proc_manager': autocomplete.ModelSelect2(url='users:user-autocomplete')
        }
