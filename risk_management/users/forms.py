from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Reset
from crispy_forms.bootstrap import InlineRadios, FormActions

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse


from .models import User


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('users:update')
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'
        self.helper.layout = Layout(
            Fieldset(
                _('Informations personnelles'),
                InlineRadios('civilite'),
                'first_name',
                'last_name'
            ),
            Fieldset(
                _('Informations professionnelles'),
                'business_unit',
                'fonction',
                'email',
                'telephone',
            ),
            FormActions(
                Submit('save', _('Sauvegarder')),
                Reset('reset', _('Rétablir'))
            )
        )

    class Meta:
        model = User
        fields = ['email', 'civilite', 'first_name', 'last_name',
                  'business_unit', 'fonction', 'telephone']

    def signup(self, request, user):
        pass


class UserUpdateForm(UserForm):

    class Meta(UserForm.Meta):
        fields = ['civilite', 'first_name', 'last_name',
                  'business_unit', 'fonction', 'telephone']






