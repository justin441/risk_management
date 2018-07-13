from django.shortcuts import render
from fm.views import AjaxCreateView, AjaxUpdateView, AjaxDeleteView
from dal import autocomplete

from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse

from risk_management.users.models import BusinessUnit
from .models import (ActiviteRisque, ProcessusRisque, Processus, Activite, Risque)
from .forms import (CreateProcessForm, CreateActivityForm, CreateProcessOutputDataForm, AddInputDataForm,
                    AddProcessusrisqueForm)

# Create your views here.


class BusinessUnitRiskRegisterView(DetailView):
    model = BusinessUnit
    template_name = 'risk_register/detail_business_unit.html'
    context_object_name = 'bu'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activiterisques'] = ActiviteRisque.objects.filter(
            activite__processus__business_unit=self.get_object()
        )
        context['processusrisques'] = ProcessusRisque.objects.filter(
            processus__business_unit=self.get_object()
        )
        return context


class ProcessusRiskRegisterView(DetailView):
    model = Processus
    template_name = 'risk_register/detail_processus.html'
    context_object_name = 'processus'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['processusrisques'] = ProcessusRisque.objects.filter(processus=self.get_object())
        context['activiterisques'] = ActiviteRisque.objects.filter(activite__processus=self.get_object())
        return context


class ActiviteRiskRegisterView(DetailView):
    model = Activite
    template_name = 'risk_register/detail_activite.html'
    context_object_name = 'activite'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activiterisques'] = ActiviteRisque.objects.filter(activite=self.get_object())
        return context


class CreateProcessView(AjaxCreateView):
    form_class = CreateProcessForm
    message_template = 'risk_register/process_card.html'

    def pre_save(self):
        self.object.business_unit = get_object_or_404(BusinessUnit, denomination=self.kwargs['business_unit'])

    def get_message_template_context(self):
        msg_ctx = super().get_message_template_context()
        msg_ctx['processus'] = self.object
        return msg_ctx

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['bu'] = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        return kwargs


class UpdateProcessView(AjaxUpdateView):
    form_class = CreateProcessForm
    model = Processus


class DeleteProcessView(AjaxDeleteView):
    model = Processus
    template_name = 'risk_register/confirmer_suppression_processus.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activites'] = Activite.objects.filter(processus=self.get_object(), status='pending')
        context['risques'] = ProcessusRisque.objects.filter(processus=self.get_object(), verifie='verified')
        context['processus'] = self.get_object()
        return context


class CreateActiviteView(AjaxCreateView):
    form_class = CreateActivityForm
    message_template = 'risk_register/activity_card.html'

    def pre_save(self):
        self.object.processus = get_object_or_404(Processus, code_processus=self.kwargs['processus'])

    def get_message_template_context(self):
        msg_ctx = super().get_message_template_context()
        msg_ctx['activite'] = self.object
        return msg_ctx


class UpdateActiviteView(AjaxUpdateView):
    form_class = CreateActivityForm
    model = Activite


class DeleteActiviteView(AjaxDeleteView):
    model = Activite
    template_name = 'risk_register/confirmer_suppression_activite.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['risques'] = ActiviteRisque.objects.filter(activite=self.get_object(), verifie='verified')
        context['activite'] = self.get_object()
        return context


class CreateProcessOutputView(AjaxCreateView):
    form_class = CreateProcessOutputDataForm

    def get_message_template_context(self):
        msg_ctx = super().get_message_template_context()
        msg_ctx['dataprocess'] = self.object
        return msg_ctx

    def pre_save(self):
        self.object.origine = get_object_or_404(Processus, pk=self.kwargs['processus'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['processus'] = get_object_or_404(Processus, pk=self.kwargs['processus'])
        return kwargs


class AddProcessInputView(AjaxUpdateView):
    form_class = AddInputDataForm
    model = Processus
    pk_url_kwarg = 'processus'


class RiskAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Risque.objects.none()

        qs = Risque.objects.all()

        classe = self.forwarded.get('classe_de_risque', None)

        if classe:
            qs = qs.filter(classe=classe)

        if self.q:
            qs = qs.filter(description__icontains=self.q)

        return qs


class NewRiskForProcessView(AjaxCreateView):
    form_class = None


class AddProcessusrisqueView(AjaxCreateView):
    form_class = AddProcessusrisqueForm
    pk_url_kwarg = 'processus'

    def pre_save(self):
        self.object.processus = get_object_or_404(Processus, pk=self.kwargs['processus'])
        self.object.soumis_par = self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['processus'] = get_object_or_404(Processus, pk=self.kwargs['processus'])
        return kwargs


class EditProcessusrisqueView(AjaxUpdateView):
    model = ProcessusRisque


class DeleteProcessusrisqueView(AjaxDeleteView):
    model = ProcessusRisque


class NewRiskForActivityView(AjaxCreateView):
    form_class = None


class AddActiviterisqueView(AjaxCreateView):
    form_class = None


class EditActiviterisqueView(AjaxUpdateView):
    model = ActiviteRisque


class DeleteActiviterisqueView(AjaxDeleteView):
    model = ActiviteRisque






