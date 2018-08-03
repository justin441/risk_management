from fm.views import AjaxCreateView, AjaxUpdateView, AjaxDeleteView
from dal import autocomplete

from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

from risk_management.users.models import BusinessUnit
from .models import (ActiviteRisque, ProcessusRisque, Processus, Activite, Risque, Estimation)
from .forms import (CreateProcessForm, CreateActivityForm, CreateProcessOutputDataForm, AddInputDataForm,
                    AddProcessusrisqueForm, CreateRiskForm, UpdateProcessusrisqueForm, AddActiviterisqueForm,
                    UpdateActiviterisqueForm, AddControleForm, CritereRisqueForm, AssignActiviterisqueForm, AssignProcessusrisqueForm,
                    ChangeActiviterisqueReviewDateForm, ChangeProcessusrisqueReviewDateForm)


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
    form_class = CreateRiskForm
    pk_url_kwarg = 'processus'

    def pre_save(self):
        self.object.cree_par = self.request.user

    def post_save(self):
        processus = get_object_or_404(Processus, pk=self.kwargs['processus'])
        pr = processus.processusrisque_set.create(
            type_de_risque=self.tr,
            risque=self.object,
            soumis_par=self.request.user,
        )
        pr.suivi_par.add(self.request.user)

    def form_valid(self, form):
        self.tr = form.data.get('type_de_risque')
        return super().form_valid(form)


class RiskDetailView(DetailView):
    model = Risque
    template_name = 'risk_register/detail_risque.html'
    context_object_name = 'risque'


class AddProcessusrisqueView(AjaxCreateView):
    form_class = AddProcessusrisqueForm
    pk_url_kwarg = 'processus'

    def pre_save(self):
        self.object.processus = get_object_or_404(Processus, pk=self.kwargs['processus'])
        self.object.soumis_par = self.request.user

    def post_save(self):
        self.object.suivi_par.add(self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['processus'] = get_object_or_404(Processus, pk=self.kwargs['processus'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['processus'] = get_object_or_404(Processus, pk=self.kwargs['processus'])
        return context


class EditProcessusrisqueView(AjaxUpdateView):
    model = ProcessusRisque
    form_class = UpdateProcessusrisqueForm
    pk_url_kwarg = 'processusrisque'

    def pre_save(self):
        self.object.modifie_par = self.request.user


class DeleteProcessusrisqueView(AjaxDeleteView):
    model = ProcessusRisque
    pk_url_kwarg = 'processusrisque'
    template_name = 'risk_register/confirmer_suppression_processusrisque.html'
    context_object_name = 'processusrisque'


class NewRiskForActivityView(AjaxCreateView):
    form_class = CreateRiskForm
    pk_url_kwarg = 'activite'

    def pre_save(self):
        self.object.cree_par = self.request.user

    def post_save(self):
        activite = get_object_or_404(Activite, pk=self.kwargs['activite'])
        ar = activite.activiterisque_set.create(
            type_de_risque=self.tr,
            risque=self.object,
            soumis_par=self.request.user
        )
        ar.suivi_par.add(self.request.user)

    def form_valid(self, form):
        self.tr = form.data.get('type_de_risque')
        return super().form_valid(form)


class AddActiviterisqueView(AjaxCreateView):
    form_class = AddActiviterisqueForm
    pk_url_kwarg = 'activite'

    def pre_save(self):
        self.object.activite = get_object_or_404(Activite, pk=self.kwargs['activite'])
        self.object.soumis_par = self.request.user

    def post_save(self):
        self.object.suivi_par.add(self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['activite'] = get_object_or_404(Activite, pk=self.kwargs['activite'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activite'] = get_object_or_404(Activite, pk=self.kwargs['activite'])
        return context


class EditActiviterisqueView(AjaxUpdateView):
    model = ActiviteRisque
    form_class = UpdateActiviterisqueForm
    pk_url_kwarg = 'activiterisque'

    def pre_save(self):
        self.object.modifie_par = self.request.user


class DeleteActiviterisqueView(AjaxDeleteView):
    model = ActiviteRisque
    pk_url_kwarg = 'activiterisque'
    template_name = 'risk_register/confirmer_suppression_activiterisque.html'
    context_object_name = 'activiterisque'


class AddControlMixin(AjaxCreateView):
    form_class = AddControleForm


class AddProcessusrisqueControleView(AddControlMixin):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['processusrisque'] = get_object_or_404(ProcessusRisque, pk=self.kwargs['processusrisque'])
        return kwargs

    def pre_save(self):
        self.object.cree_par = self.request.user
        self.object.content_object = get_object_or_404(ProcessusRisque, pk=self.kwargs['processusrisque'])


class AddActiviterisqueControle(AddControlMixin):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['activiterisque'] = get_object_or_404(ActiviteRisque, pk=self.kwargs['activiterisque'])
        return kwargs

    def pre_save(self):
        self.object.cree_par = self.request.user
        self.object.content_object = get_object_or_404(ActiviteRisque, pk=self.kwargs['activiterisque'])


class SetSeuilProcessusrisqueView(AjaxCreateView):
    form_class = CritereRisqueForm
    pk_url_kwarg = 'processusrisque'

    def pre_save(self):
        self.object.evalue_par = self.request.user
        self.object.modifie_par = self.request.user

    def post_save(self):
        processusrisque = get_object_or_404(ProcessusRisque, pk=self.kwargs['processusrisque'])
        if processusrisque.criterisation:
            processusrisque.criterisation.delete()
        processusrisque.criterisation = self.object
        processusrisque.save()


class ProcessusrisqueEstimationView(AjaxCreateView):
    form_class = CritereRisqueForm
    pk_url_kwarg = 'processusrisque'

    def pre_save(self):
        self.object.evalue_par = self.request.user

    def post_save(self):
        processusrisque = get_object_or_404(ProcessusRisque, pk=self.kwargs['processusrisque'])
        Estimation.objects.create(
            criterisation=self.object,
            content_object=processusrisque,
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['processusrisque'] = get_object_or_404(ProcessusRisque, pk=self.kwargs['processusrisque'])
        return kwargs


class SetSeuilActiviterisqueView(AjaxCreateView):
    form_class = CritereRisqueForm
    pk_url_kwarg = 'activiterisque'

    def pre_save(self):
        self.object.evalue_par = self.request.user
        self.object.modifie_par = self.request.user

    def post_save(self):
        activiterisque = get_object_or_404(ActiviteRisque, pk=self.kwargs['activiterisque'])
        if activiterisque.criterisation:
            activiterisque.criterisation.delete()
        activiterisque.criterisation = self.object
        activiterisque.save()


class ActiviterisqueEstimationView(AjaxCreateView):
    form_class = CritereRisqueForm
    pk_url_kwarg = 'activiterisque'

    def pre_save(self):
        self.object.evalue_par = self.request.user

    def post_save(self):
        activiterisque = get_object_or_404(ActiviteRisque, pk=self.kwargs['activiterisque'])
        Estimation.objects.create(
            criterisation=self.object,
            content_object=activiterisque
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['activiterisque'] = get_object_or_404(ActiviteRisque, pk=self.kwargs['activiterisque'])
        return kwargs


class AssignerActiviterisqueView(AjaxUpdateView):
    form_class = AssignActiviterisqueForm
    pk_url_kwarg = 'activiterisque'
    model = ActiviteRisque

    def pre_save(self):
        self.object.modifie_par = self.request.user


class AssignerProcessusrisqueView(AjaxUpdateView):
    form_class = AssignProcessusrisqueForm
    pk_url_kwarg = 'processusrisque'
    model = ProcessusRisque

    def pre_save(self):
        self.object.modifie_par = self.request.user


class SetProcessusrisqueReviewDate(AjaxUpdateView):
    form_class = ChangeProcessusrisqueReviewDateForm
    pk_url_kwarg = 'processusrisque'
    model = ProcessusRisque

    def pre_save(self):
        self.object.modifie_par = self.request.user


class SetActiviterisqueReviewDate(AjaxUpdateView):
    form_class = ChangeActiviterisqueReviewDateForm
    pk_url_kwarg = 'activiterisque'
    model = ActiviteRisque

    def pre_save(self):
        self.object.modifie_par = self.request.user


def checkriskstatus(request, pk):
    if request.is_ajax():
        data = {}
        try:
            risque = ProcessusRisque.objects.get(pk=pk)
        except ProcessusRisque.DoesNotExist:
            try:
                risque = ActiviteRisque.objects.get(pk=pk)
            except ActiviteRisque.DoesNotExist:
                data['error_message'] = _('Aucun risque trouvé')
                data['result'] = 'Failure'

            else:
                data['verifie'] = risque.verifie
                data['result'] = 'Success'
        else:
            data['verifie'] = risque.verifie
            data['result'] = 'Success'

        return JsonResponse(data)


def changeriskstatus(request, pk):
    if request.method == 'POST' and request.is_ajax():
        data = {}
        try:
            risque = ProcessusRisque.objects.get(pk=pk)
        except ProcessusRisque.DoesNotExist:
            try:
                risque = ActiviteRisque.objects.get(pk=pk)
            except ActiviteRisque.DoesNotExist:
                risque = None
                data['error_message'] = _('Aucun risque trouvé')
                data['result'] = 'Failure'
        if risque:
            if risque.verifie != request.POST.get('verifie'):
                data['result'] = 'Failure'
                data['error_message'] = _('statut du risque désynchronisé.')
            elif request.POST.get('verifie') == 'pending':
                risque.verifie = 'verified'
                risque.save()
                data['result'] = 'success'
            elif request.POST.get('verifie') == 'verified':
                risque.verifie = 'pending'
                risque.save()
                data['result'] = 'success'
            else:
                data['result'] = 'Failure'
                data['error_message'] = _('status du risque inconnu')

        return JsonResponse(data)







