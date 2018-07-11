from dal import autocomplete
from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from .models import (Processus, Activite)


class CreateProcessForm(forms.ModelForm):
    class Meta:
        model = Processus
        exclude = ['business_unit', 'input_data']
        widgets = {
            'proc_manager': autocomplete.ModelSelect2(url='users:user-autocomplete')
        }


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
