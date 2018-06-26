from django.shortcuts import render
from django.views.generic import DetailView

from .models import (BusinessUnit,)

# Create your views here.


class BusinessUnitDetailView(DetailView):
    model = BusinessUnit
    template_name = 'risk_register/detail_business_unit.html'
    context_object_name = 'bu'
