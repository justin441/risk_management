from dal import autocomplete
from datetime import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML, Field
from crispy_forms.bootstrap import InlineRadios

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from .models import (Processus, Activite, ProcessData, ProcessusRisque, ClasseDeRisques,
                     Risque, ActiviteRisque, Controle, CritereDuRisque, Estimation)


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
            'proc_manager': autocomplete.ModelSelect2(url='users:user-autocomplete',
                                                      attrs={
                                                          'data-placeholder': _('Nom ou prénom'),
                                                          'data-allow-clear': 'true',
                                                          'data-width': '100%',
                                                      }
                                                      ),
            'description': forms.Textarea(attrs={
                'rows': 5,
                'style': 'resize: none'
            })
        }

    def clean_nom(self):
        # le nom du processus doit être unique pour un business_unit
        nom = self.cleaned_data['nom']
        try:
            try:
                # si le formulaire est utilisé pour modifier un processus
                Processus.objects.get(nom=nom, business_unit=self.instance.business_unit)
            except AttributeError:
                # si le formulaire est utilisé pour créer un processus
                Processus.objects.get(nom=nom, business_unit=self.bu)
        except Processus.DoesNotExist:
            return nom
        else:
            if Processus.objects.get(nom=nom, business_unit=self.instance.business_unit) == self.instance:
                return nom
            else:
                msg = _('Un processus portant ce nom existe déjà.')
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
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'
        processus = self.instance
        q = ProcessData.objects.filter(origine__business_unit=processus.business_unit)
        self.fields['input_data'].queryset = q.exclude(origine=processus)


class CreateActivityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start'].label = 'début'
        self.fields['start'].initial = datetime(now().year, 1, 1)
        self.fields['end'].label = 'fin'
        self.fields['end'].initial = datetime(now().year, 12, 31)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'

    class Meta:
        model = Activite
        fields = ['nom', 'description', 'start', 'end', 'responsable']
        widgets = {
            'responsable': autocomplete.ModelSelect2(url='users:user-autocomplete',
                                                     attrs={
                                                         'data-placeholder': _('Nom ou prénom'),
                                                         'data-allow-clear': 'true',
                                                         'data-width': '100%',
                                                     }),
            'description': forms.Textarea(attrs={'rows': 3, 'style': 'resize: none;'}),
            'start': forms.SelectDateWidget(),
            'end': forms.SelectDateWidget()
        }

    def clean(self):
        cleaned_data = super().clean()
        debut = cleaned_data.get('start', '')
        fin = cleaned_data.get('end', '')
        if debut > fin:
            msg = _('La date de début est postérieure à la date de fin.')
            self.add_error('start', msg)
            self.add_error('end', msg)
        return cleaned_data


class CreateProcessOutputDataForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.processus = kwargs.pop('processus')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'

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


class ProcessusrisqueBaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'

    class Meta:
        model = ProcessusRisque
        fields = ['risque', 'type_de_risque']
        widgets = {
            'risque': autocomplete.ModelSelect2(url='risk_register:risque-autocomplete',
                                                forward=['classe_de_risque'],
                                                attrs={
                                                    'data-placeholder': _('Description'),
                                                    'data-allow-clear': 'true',
                                                    'data-width': '100%',

                                                }
                                                )
        }


class AddProcessusrisqueForm(ProcessusrisqueBaseForm):
    classe_de_risque = forms.ModelChoiceField(queryset=ClasseDeRisques.objects.all(),
                                              required=False)

    def __init__(self, *args, **kwargs):
        self.processus = kwargs.pop('processus', '')
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(
                _('Rechercher un risque'),
                'classe_de_risque',
                'risque',
                HTML(
                    """ <div id="detail-risque"></div>"""
                )

            ),
            InlineRadios('type_de_risque'),
            Fieldset(
                _('Créer un risque'),
                HTML(
                    """{% load i18n %}
                    <div class="offset-md-4 col-md-8">
                        <a href="{% url 'risk_register:creer_risque_processus' processus=processus.pk %}"
                        class='fa fa-plus fm-create text-info' data-fm-head="{% trans 'Créer un risque' %}"
                        data-fm-callback="reload">
                            {% trans ' Nouveau risque' %}
                        </a>
                    </div>"""
                ),
            )

        )

    class Meta(ProcessusrisqueBaseForm.Meta):
        fields = ['classe_de_risque', 'type_de_risque', 'risque']

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


class UpdateProcessusrisqueForm(ProcessusrisqueBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(
                _('Rechercher un risque'),
                'risque',
                HTML(
                    """<div id='detail-risque'></div> """
                ),
            ),
            InlineRadios('type_de_risque')
        )

    class Meta(ProcessusrisqueBaseForm.Meta):
        fields = ['risque', 'type_de_risque']


class CreateRiskForm(forms.ModelForm):
    type_de_risque = forms.ChoiceField(label=_('type de risque'), choices=(
        ('O', _('opportunité')),
        ('M', _('menace')),
    ), initial='M')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'
        self.helper.layout = Layout(
            InlineRadios('type_de_risque'),
            Fieldset(
                _('Risque'),
                'classe',
                'nom',
                'description',
                'cause',
                'consequence'
            )
        )

    class Meta:
        model = Risque
        fields = ['type_de_risque', 'classe', 'nom', 'description', 'cause', 'consequence']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 5,
                'style': 'resize: none'
            }),
            'cause': forms.Textarea(attrs={
                'rows': 5,
                'style': 'resize: none'
            }),
            'consequence': forms.Textarea(attrs={
                'rows': 5,
                'style': 'resize: none'
            })
        }


class ActiviterisqueBaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'

    class Meta:
        model = ActiviteRisque
        fields = ['risque', 'type_de_risque']
        widgets = {
            'risque': autocomplete.ModelSelect2(url='risk_register:risque-autocomplete',
                                                forward=['classe_de_risque'],
                                                attrs={
                                                    'data-placeholder': _('Description'),
                                                    'data-allow-clear': 'true',
                                                    'data-width': '100%',

                                                }
                                                )
        }


class AddActiviterisqueForm(ActiviterisqueBaseForm):
    classe_de_risque = forms.ModelChoiceField(queryset=ClasseDeRisques.objects.all(),
                                              required=False)

    def __init__(self, *args, **kwargs):
        self.activite = kwargs.pop('activite', '')
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(
                _('Rechercher un risque'),
                'classe_de_risque',
                'risque',
                HTML(
                    """ <div id="detail-risque"></div>"""
                )

            ),
            InlineRadios('type_de_risque'),
            Fieldset(
                _('Créer un risque'),
                HTML(
                    """{% load i18n %}
                    <div class="offset-md-4 col-md-8">
                        <a href="{% url 'risk_register:creer_risque_activite' activite=activite.pk %}"
                        class='fa fa-plus fm-create text-info' data-fm-head="{% trans 'Créer un risque' %}"
                        data-fm-callback="reload">
                            {% trans ' Nouveau risque' %}
                        </a>
                    </div>"""
                ),
            )

        )

    class Meta(ActiviterisqueBaseForm.Meta):
        fields = ['classe_de_risque', 'type_de_risque', 'risque']

    def clean(self):
        """Verifier qu'un même risque n'est pas soumis plusieurs fois"""
        cleaned_data = super().clean()
        cleaned_data.pop('classe_de_risque')
        risque = cleaned_data.get('risque', '')
        type_de_risque = cleaned_data.get('type_de_risque', '')
        try:
            ActiviteRisque.objects.get(risque=risque, activite=self.activite, type_de_risque=type_de_risque)
        except ActiviteRisque.DoesNotExist:
            return cleaned_data
        else:
            if ActiviteRisque.objects.get(risque=risque, activite=self.activite,
                                          type_de_risque=type_de_risque) == self.instance:
                return cleaned_data
            else:
                msg = _('Ce risque a déjà été rapporté')
                self.add_error('risque', msg)


class UpdateActiviterisqueForm(ActiviterisqueBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(
                _('Rechercher un risque'),
                'risque',
                HTML(
                    """<div id='detail-risque'></div> """
                ),
            ),
            InlineRadios('type_de_risque')
        )

    class Meta(ActiviterisqueBaseForm.Meta):
        fields = ['risque', 'type_de_risque']


class AddControleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.processusrisque = kwargs.pop('processusrisque', None)
        self.activiterisque = kwargs.pop('activiterisque', None)
        super().__init__(*args, **kwargs)
        self.fields['description'].required = True
        self.helper = FormHelper
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'
        self.helper.layout = Layout(
            InlineRadios('critere_cible'),
            'nom',
            'description'
        )

    class Meta:
        model = Controle
        fields = ['critere_cible', 'nom', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'style': 'resize: none;'})
        }

    def clean(self):
        if self.processusrisque:
            if not self.processusrisque.estimations.all():
                msg = _('Ce risque n\'a pas encore été estimé; impossible d\'y ajouter un contrôle')
                self.add_error(None, msg)
            elif self.processusrisque.estimations.latest().est_obsolete or self.processusrisque.est_obsolete:
                msg = _('Les données du risque sont obsolètes; impossible d\'y ajouter un contrôle')
                self.add_error(None, msg)
        if self.activiterisque:
            if not self.activiterisque.estimations.all():
                msg = _('Ce risque n\'a pas encore été estimé; impossible d\'y ajouter un contrôle')
                self.add_error(None, msg)
            elif self.activiterisque.estimations.latest().est_obsolete or self.activiterisque.est_obsolete:
                msg = _('Les données du risque sont obsolètes; impossible d\'y ajouter un contrôle')
                self.add_error(None, msg)
        cleaned_data = super().clean()
        return cleaned_data


class EditControleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start'].label = _('Début')
        self.fields['end'].label = _('Fin')
        self.fields['description'].required = True
        self.helper = FormHelper
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'
        self.helper.layout = Layout(
            InlineRadios('critere_cible'),
            'nom',
            'description',
            'start',
            'end'
        )

    class Meta:
        model = Controle
        fields = ['critere_cible', 'nom', 'start', 'end', 'description']
        widgets = {
            'start': forms.SelectDateWidget,
            'end': forms.SelectDateWidget,
            'description': forms.Textarea(attrs={'rows': 5, 'style': 'resize: none;'})
        }

    def clean(self):
        cleaned_data = super().clean()
        debut = cleaned_data.get('start', '')
        fin = cleaned_data.get('end', '')
        if (debut and fin) and (fin < debut):
            msg = _('La date de début est postérieure à la date de fin.')
            self.add_error('start', msg)
            self.add_error('end', msg)
        return cleaned_data


class CritereRisqueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.processusrisque = kwargs.pop('processusrisque', None)
        self.activiterisque = kwargs.pop('activiterisque', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'

    class Meta:
        model = CritereDuRisque
        fields = ['detectabilite', 'severite', 'occurence']

    def clean(self):
        if (self.processusrisque and
            self.processusrisque.verifie == "pending") or (self.activiterisque and
                                                           self.activiterisque.verifie == 'pending'):
            msg = _('Ce risque n\'a pas encore été vérifié; impossible de l\'estimer.')
            self.add_error(None, msg)
        return super().clean()


class AssignRiskform(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'
        self.helper.layout = Layout(
            'proprietaire',
            HTML(
                '<div id="user-info"></div>'
            )
        )
        self.fields['proprietaire'].label = _('Employé')

    class Meta:
        fields = ['proprietaire']
        widgets = {
            'proprietaire': autocomplete.ModelSelect2(url='users:user-autocomplete',
                                                      attrs={
                                                          'data-placeholder': _('Nom ou prénom'),
                                                          'data-allow-clear': 'true',
                                                          'data-width': '100%',
                                                      }
                                                      ),
        }


class AssignActiviterisqueForm(AssignRiskform):
    class Meta(AssignRiskform.Meta):
        model = ActiviteRisque


class AssignProcessusrisqueForm(AssignRiskform):
    class Meta(AssignRiskform.Meta):
        model = ProcessusRisque


class ChangeReviewDateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'

    class Meta:
       fields = ['date_revue']
       widgets = {
           'date_revue': forms.SelectDateWidget()
       }


class ChangeProcessusrisqueReviewDateForm(ChangeReviewDateForm):
    class Meta(ChangeReviewDateForm.Meta):
        model = ProcessusRisque


class ChangeActiviterisqueReviewDateForm(ChangeReviewDateForm):
    class Meta(ChangeReviewDateForm.Meta):
        model = ActiviteRisque


class AssignControlform(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'
        self.helper.layout = Layout(
            Field('assigne_a', id='id_proprietaire'),
            HTML(
                '<div id="user-info"></div>'
            )
        )
        self.fields['assigne_a'].label = _('Employé')

    class Meta:
        fields = ['assigne_a']
        model = Controle
        widgets = {
            'proprietaire': autocomplete.ModelSelect2(url='users:user-autocomplete',
                                                      attrs={
                                                          'data-placeholder': _('Nom ou prénom'),
                                                          'data-allow-clear': 'true',
                                                          'data-width': '100%',
                                                      }
                                                      ),
        }
