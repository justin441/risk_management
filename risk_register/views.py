from django.shortcuts import render
from django.views.generic import DetailView

from .models import (BusinessUnit, ActiviteRisque, ProcessusRisque)

# Create your views here.


class BusinessUnitDetailView(DetailView):
    model = BusinessUnit
    template_name = 'risk_register/detail_business_unit.html'
    context_object_name = 'bu'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activiterisques'] = ActiviteRisque.objects.filter(
            activite__processus__business_unit=self.get_object()
        ).filter(verifie='verified')
        context['processusrisques'] = ProcessusRisque.objects.filter(
            processus__business_unit=self.get_object()
        ).filter(verifie='verified')
        return context
