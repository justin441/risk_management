from dal import autocomplete
from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from .models import (Processus, Activite, ProcessData)


class CreateProcessForm(forms.ModelForm):
    class Meta:
        model = Processus
        exclude = ['business_unit', 'input_data']
        widgets = {
            'proc_manager': autocomplete.ModelSelect2(url='users:user-autocomplete'),
        }


class AddInputDataForm(forms.ModelForm):
    class Meta:
        model = Processus
        widgets = {
            'input_data': forms.CheckboxSelectMultiple(),
        }
        fields = ['input_data']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        processus = self.instance
        q = ProcessData.objects.filter(origine__business_unit=processus.business_unit)
        self.fields['input_data'].queryset = q.exclude(origine=processus)


class CreateActivityForm(forms.ModelForm):

    start = forms.DateTimeField(label=_('debut'), initial=datetime(now().year, 1, 1),  widget=forms.SelectDateWidget())
    end = forms.DateTimeField(label=_('fin'), initial=datetime(now().year, 12, 31), widget=forms.SelectDateWidget())

    class Meta:
        model = Activite
        fields = ['start', 'end', 'nom', 'description', 'responsable']
        widgets = {
            'responsable': autocomplete.ModelSelect2(url='users:user-autocomplete'),
            'nom': forms.TextInput(attrs={'size': 80}),
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 3, 'style': 'resize: none;'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start', '')
        end = cleaned_data.get('end', '')
        if start > end:
            msg = _('La date de debut est postérieure à la date de fin.')
            raise forms.ValidationError(msg)
        return cleaned_data


class CreateProcessOutputDataForm(forms.ModelForm):
    class Meta:
        model = ProcessData
        fields = ['nom']
