from django.shortcuts import render
from fm.views import AjaxCreateView

from django.views.generic import DetailView
from django.shortcuts import get_object_or_404

from risk_management.users.models import BusinessUnit
from .models import (ActiviteRisque, ProcessusRisque, Processus, Activite)
from .forms import CreateProcessForm

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
