from dal import autocomplete
from datetime import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset
from crispy_forms.bootstrap import InlineRadios

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.db.models import Q

from .models import (Processus, Activite, ProcessData, ProcessusRisque, ClasseDeRisques)


class CreateProcessForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.bu = kwargs.pop('bu', '')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'

    class Meta:
        model = Processus
        exclude = ['business_unit', 'input_data']
        widgets = {
            'proc_manager': autocomplete.ModelSelect2(url='users:user-autocomplete'),
            'description': forms.Textarea(attrs={
                'rows': 5,
                'style': 'resize: none'
            })
        }

    def clean_nom(self):
        # le nom du processus doit être unique pour un business_unit
        nom = self.cleaned_data['nom']
        try:
            if hasattr(self.instance, 'business_unit'):
                Processus.objects.get(nom=nom, business_unit=self.instance.business_unit)
            else:
                Processus.objects.get(nom=nom, business_unit=self.bu)
        except Processus.DoesNotExist:
            return nom
        else:
            if Processus.objects.get(nom=nom, business_unit=self.instance.business_unit) == self.instance:
                return nom
            else:
                msg = _('Un processus portant ce nom existe déjà')
                raise forms.ValidationError(msg)


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
    start = forms.DateTimeField(label=_('debut'), initial=datetime(now().year, 1, 1), widget=forms.SelectDateWidget())
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
    def __init__(self, *args, **kwargs):
        self.processus = kwargs.pop('processus')
        super().__init__(*args, **kwargs)

    class Meta:
        model = ProcessData
        fields = ['nom']

    def clean_nom(self):
        # la donnée de sortie doit avoir un nom unique dans le processus
        nom = self.cleaned_data['nom']
        try:
            ProcessData.objects.get(nom=nom, origine=self.processus)
        except ProcessData.DoesNotExist:
            return nom
        else:
            if ProcessData.objects.get(nom=nom, origine=self.processus) == self.instance:
                return nom
            else:
                msg = _('Une donnée de sortie portant ce nom existe déja')
                raise forms.ValidationError(msg)


class AddProcessusrisqueForm(forms.ModelForm):
    classe_de_risque = forms.ModelChoiceField(queryset=ClasseDeRisques.objects.all(),
                                              required=False)

    def __init__(self, *args, **kwargs):
        self.processus = kwargs.pop('processus')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'
        self.helper.layout = Layout(
            Fieldset(
                _('Rechercher un risque'),
                'classe_de_risque',
                'risque',
            ),
            InlineRadios('type_de_risque')

        )

    class Meta:
        model = ProcessusRisque
        fields = ['classe_de_risque', 'type_de_risque', 'risque']
        widgets = {
            'risque': autocomplete.ModelSelect2(url='risk_register:risque-autocomplete',
                                                forward=['classe_de_risque'],
                                                attrs={
                                                    'data-placeholder': _('Description')
                                                }
                                                )
        }

    def clean(self):
        """Verifier qu'un même risque n'est pas soumis plusieurs fois"""
        cleaned_data = super().clean()
        cleaned_data.pop('classe_de_risque')
        risque = cleaned_data.get('risque', '')
        type_de_risque = cleaned_data.get('type_de_risque', '')
        try:
            ProcessusRisque.objects.get(risque=risque, processus=self.processus, type_de_risque=type_de_risque)
        except ProcessusRisque.DoesNotExist:
            return cleaned_data
        else:
            if ProcessusRisque.objects.get(risque=risque, processus=self.processus,
                                           type_de_risque=type_de_risque) == self.instance:
                return cleaned_data
            else:
                msg = _('Ce risque a déjà été rapporté')
                self.add_error('risque', msg)
