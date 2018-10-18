import datetime
import logging

from fm.views import AjaxCreateView, AjaxUpdateView, AjaxDeleteView
from dal import autocomplete
from rules.contrib.views import PermissionRequiredMixin, permission_required, objectgetter

from django.views.generic import DetailView, ListView
from django.core.exceptions import PermissionDenied
from django.db.models import F, Count
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.forms.utils import from_current_timezone
from django.core.mail import send_mail

from risk_management.users.models import BusinessUnit
from .models import (ActiviteRisque, ProcessusRisque, Processus, Activite, Risque,
                     Controle)
from .forms import (CreateProcessForm, CreateActivityForm, CreateProcessOutputDataForm, AddInputDataForm,
                    AddProcessusrisqueForm, CreateRiskForm, UpdateProcessusrisqueForm, AddActiviterisqueForm,
                    UpdateActiviterisqueForm, AddControleForm, CritereRisqueForm, AssignActiviterisqueForm,
                    AssignProcessusrisqueForm, EditControleForm, UpdateRiskForm, CreateInputDataForm,
                    ChangeActiviterisqueReviewDateForm, ChangeProcessusrisqueReviewDateForm, AssignControlform,
                    EstimationRisqueForm)
from risk_management.users.utils import get_risk_occurrences, get_changes_between_2_objects

logger = logging.getLogger('my view_logger')


# Create your views here.

class RiskClassView(ListView):
    paginate_by = 20
    context_object_name = 'risks_list'
    template_name = 'risk_register/liste_risques.html'

    def get_queryset(self):
        return Risque.objects.filter(
            classe__nom=self.kwargs['classe']).annotate(nb_risques=Count('processusrisque') + Count('activiterisque'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_name'] = self.kwargs['classe']
        return context


class RiskOccurrencesView(ListView):
    paginate_by = 10
    context_object_name = 'risk_occurrences'
    template_name = 'risk_register/risk_occurrences.html'

    def get_queryset(self):
        risque = get_object_or_404(Risque, pk=self.kwargs['risque'])
        return get_risk_occurrences(risque)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['risque'] = get_object_or_404(Risque, pk=self.kwargs['risque'])
        return context


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


class CreateProcessView(PermissionRequiredMixin, AjaxCreateView):
    form_class = CreateProcessForm
    message_template = 'risk_register/process_card.html'
    permission_required = 'users.add_process_to_bu'
    success_message = 'Le processus "%(nom)" a été ajouté avec succès.'

    def pre_save(self):
        self.object.business_unit = get_object_or_404(BusinessUnit, denomination=self.kwargs['business_unit'])
        logger.info('Saving process %s in %s' % (str(self.object), self.object.business_unit))

    def post_save(self):
        logger.info('New process \'%s\' created' % str(self.object.nom))
        self.object.issue_notification('create', actor=self.request.user, target=self.object)
        logger.info('Notification sent')

    def get_message_template_context(self):
        msg_ctx = super().get_message_template_context()
        msg_ctx['processus'] = self.object
        return msg_ctx

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['bu'] = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        return kwargs

    def get_permission_object(self):
        return get_object_or_404(BusinessUnit, denomination=self.kwargs['business_unit'])


class UpdateProcessView(PermissionRequiredMixin, AjaxUpdateView):
    permission_required = 'risk_register.change_processus'
    form_class = CreateProcessForm
    model = Processus

    def pre_save(self):
        self.old_object = get_object_or_404(Processus, pk=self.object.pk)

    def post_save(self):
        exclude = [f.name for f in Processus._meta.fields if not f.name == 'proc_manager']
        if get_changes_between_2_objects(self.old_object, self.object, exclude):
            logger.info("Le manager du processus '{}' a été changé.".format(self.object.nom))
            self.object.issue_notification('change_proc_manager', actor=self.request.user, target=self.object)
            logger.info('Notification sent.')


class DeleteProcessView(PermissionRequiredMixin, AjaxDeleteView):
    model = Processus
    template_name = 'risk_register/confirmer_suppression_processus.html'
    permission_required = 'risk_register.delete_processus'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activites'] = Activite.objects.filter(processus=self.get_object(), status='pending')
        context['risques'] = ProcessusRisque.objects.filter(processus=self.get_object(), verifie='verified')
        context['processus'] = self.get_object()
        return context

    def post_delete(self):
        logger.info('Process successfully deleted.')


class CreateActiviteView(PermissionRequiredMixin, AjaxCreateView):
    form_class = CreateActivityForm
    message_template = 'risk_register/activity_card.html'
    permission_required = 'risk_register.add_activity_to_process'

    def pre_save(self):
        self.object.processus = get_object_or_404(Processus, code_processus=self.kwargs['processus'])
        logger.info('Saving activity %s in process %s' % (str(self.object), str(self.object.processus)))

    def post_save(self):
        logger.info('Activity %s saved' % self.object.nom)
        self.object.issue_notification('create', actor=self.request.user, target=self.object)

    def get_message_template_context(self):
        msg_ctx = super().get_message_template_context()
        msg_ctx['activite'] = self.object
        return msg_ctx

    def get_permission_object(self):
        return get_object_or_404(Processus, code_processus=self.kwargs['processus'])


class UpdateActiviteView(PermissionRequiredMixin, AjaxUpdateView):
    form_class = CreateActivityForm
    model = Activite
    permission_required = 'risk_register.change_activite'

    def pre_save(self):
        self.old = Activite.objects.get(pk=self.object.pk)

    def post_save(self):
        if 'status' in get_changes_between_2_objects(self.old, self.object):
            if self.object.status == 'completed':
                self.object.issue_notification('complete', actor=self.request.user, target=self.object)
            else:
                self.object.issue_notification('create', actor=self.request.user, target=self.object)


class DeleteActiviteView(PermissionRequiredMixin, AjaxDeleteView):
    model = Activite
    template_name = 'risk_register/confirmer_suppression_activite.html'
    permission_required = 'risk_register.delete_activite',

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['risques'] = ActiviteRisque.objects.filter(activite=self.get_object(), verifie='verified')
        context['activite'] = self.get_object()
        return context

    def post_delete(self):
        logger.info('Activity successfully deleted')
        self.object.issue_notification('delete', actor=self.request.user, target=self.object)


class CreateProcessOutputView(PermissionRequiredMixin, AjaxCreateView):
    permission_required = 'risk_register.add_process_data'
    form_class = CreateProcessOutputDataForm

    def get_message_template_context(self):
        msg_ctx = super().get_message_template_context()
        msg_ctx['dataprocess'] = self.object
        return msg_ctx

    def pre_save(self):
        self.object.origine = get_object_or_404(Processus, pk=self.kwargs['processus'])
        logger.info('Saving process data %s' % str(self.object))

    def post_save(self):
        logger.info('Process data %s saved successfully' % str(self.object))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['processus'] = get_object_or_404(Processus, pk=self.kwargs['processus'])
        return kwargs

    def get_permission_object(self):
        return get_object_or_404(Processus, pk=self.kwargs['processus'])


class CreateProcessInputView(PermissionRequiredMixin, AjaxCreateView):
    form_class = CreateInputDataForm
    permission_required = 'risk_register.add_process_data'

    def post_save(self):
        processus = get_object_or_404(Processus, pk=self.kwargs['processus'])
        processus.input_data.add(self.object)
        logger.info('Process data %s saved successfully' % str(self.object))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['processus'] = get_object_or_404(Processus, pk=self.kwargs['processus'])
        return kwargs

    def get_permission_object(self):
        return get_object_or_404(Processus, pk=self.kwargs['processus'])


class AddProcessInputView(PermissionRequiredMixin, AjaxUpdateView):
    form_class = AddInputDataForm
    model = Processus
    pk_url_kwarg = 'processus'
    permission_required = 'risk_register.add_process_data'


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


class NewRiskForProcessView(PermissionRequiredMixin, AjaxCreateView):
    form_class = CreateRiskForm
    pk_url_kwarg = 'processus'
    permission_required = 'risk_register.add_process_risk'

    def get_permission_object(self):
        return get_object_or_404(Processus, pk=self.kwargs['processus'])

    def pre_save(self):
        self.object.cree_par = self.request.user
        logger.info('Saving new risk: %s' % str(self.object))

    def post_save(self):
        logger.info('%s saved successfully' % str(self.object))
        self.object.issue_notification('create', actor=self.request.user, target=self.object)
        processus = get_object_or_404(Processus, pk=self.kwargs['processus'])
        logger.info("Adding '%s' to process '%s'" % (str(self.object), str(processus)))
        pr = processus.processusrisque_set.create(
            type_de_risque=self.tr,
            risque=self.object,
            soumis_par=self.request.user,
        )
        pr.issue_notification('create', actor=self.request.user, target=pr)
        logger.info("'%s' successfully added to process %s" % (str(self.object), str(processus)))
        pr.suivi_par.add(self.request.user)

    def form_valid(self, form):
        self.tr = form.data.get('type_de_risque')
        return super().form_valid(form)


class RiskDetailView(DetailView):
    model = Risque
    template_name = 'risk_register/detail_risque.html'
    context_object_name = 'risque'


class UpdateRiskView(PermissionRequiredMixin, AjaxUpdateView):
    model = Risque
    form_class = UpdateRiskForm
    permission_required = 'risk_register.change_risque'


class AddProcessusrisqueView(PermissionRequiredMixin, AjaxCreateView):
    form_class = AddProcessusrisqueForm
    pk_url_kwarg = 'processus'
    permission_required = 'risk_register.add_process_risk'

    def get_permission_object(self):
        return get_object_or_404(Processus, pk=self.kwargs['processus'])

    def pre_save(self):
        self.object.processus = get_object_or_404(Processus, pk=self.kwargs['processus'])
        self.object.soumis_par = self.request.user
        logger.info("Saving risk identification '%s'" % (str(self.object)))

    def post_save(self):
        self.object.suivi_par.add(self.request.user)
        logger.info("Risk identification '%s' saved successfully" % (str(self.object)))
        self.object.issue_notification('create', actor=self.request.user, target=self.object)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['processus'] = get_object_or_404(Processus, pk=self.kwargs['processus'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['processus'] = get_object_or_404(Processus, pk=self.kwargs['processus'])
        return context


class ProcessusrisqueDetailview(DetailView):
    model = ProcessusRisque
    context_object_name = 'risque_identif'
    template_name = 'risk_register/detail_identification_risque.html'


class EditProcessusrisqueView(PermissionRequiredMixin, AjaxUpdateView):
    permission_required = 'risk_register.change_processusrisque'
    model = ProcessusRisque
    form_class = UpdateProcessusrisqueForm
    pk_url_kwarg = 'processusrisque'

    def pre_save(self):
        self.object.modifie_par = self.request.user
        self.old = ProcessusRisque.objects.get(pk=self.object.pk)

    def post_save(self):
        if 'type_de_risque' in get_changes_between_2_objects(self.old, self.object):
            self.object.issue_notification('change_risk_type', actor=self.request.user, target=self.object)


class DeleteProcessusrisqueView(PermissionRequiredMixin, AjaxDeleteView):
    permission_required = 'risk_register.delete_processusrisque'
    model = ProcessusRisque
    pk_url_kwarg = 'processusrisque'
    template_name = 'risk_register/confirmer_suppression_processusrisque.html'
    context_object_name = 'processusrisque'

    def post_delete(self):
        logger.info("Risk '%s' deleted successfully." % str(self.object))
        self.object.issue_notification('delete', actor=self.request.user, target=self.object)


class NewRiskForActivityView(PermissionRequiredMixin, AjaxCreateView):
    permission_required = 'risk_register.add_activity_risk'
    form_class = CreateRiskForm
    pk_url_kwarg = 'activite'

    def get_permission_object(self):
        return get_object_or_404(Activite, pk=self.kwargs['activite'])

    def pre_save(self):
        self.object.cree_par = self.request.user
        logger.info('Saving new risk: %s' % str(self.object))

    def post_save(self):
        self.object.issue_notification('create', actor=self.request.user, target=self.object)
        activite = get_object_or_404(Activite, pk=self.kwargs['activite'])
        ar = activite.activiterisque_set.create(
            type_de_risque=self.tr,
            risque=self.object,
            soumis_par=self.request.user
        )
        ar.issue_notification('create', actor=self.request.user, target=ar)
        ar.suivi_par.add(self.request.user)
        logger.info("'%s' successfully added to activity %s" % (str(self.object), str(activite)))

    def form_valid(self, form):
        self.tr = form.data.get('type_de_risque')
        return super().form_valid(form)


class AddActiviterisqueView(PermissionRequiredMixin, AjaxCreateView):
    permission_required = 'risk_register.add_activity_risk'
    form_class = AddActiviterisqueForm
    pk_url_kwarg = 'activite'

    def get_permission_object(self):
        return get_object_or_404(Activite, pk=self.kwargs['activite'])

    def pre_save(self):
        self.object.activite = get_object_or_404(Activite, pk=self.kwargs['activite'])
        self.object.soumis_par = self.request.user
        logger.info("Saving '%s'" % str(self.object))

    def post_save(self):
        self.object.suivi_par.add(self.request.user)
        logger.info("'%s' Saved successfully" % str(self.object))
        self.object.issue_notification('create', actor=self.request.user, target=self.object)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['activite'] = get_object_or_404(Activite, pk=self.kwargs['activite'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activite'] = get_object_or_404(Activite, pk=self.kwargs['activite'])
        return context


class ActiviterisqueDetailView(DetailView):
    model = ActiviteRisque
    context_object_name = 'risque_identif'
    template_name = 'risk_register/detail_identification_risque.html'


class EditActiviterisqueView(PermissionRequiredMixin, AjaxUpdateView):
    permission_required = 'risk_register.change_activiterisque'
    model = ActiviteRisque
    form_class = UpdateActiviterisqueForm
    pk_url_kwarg = 'activiterisque'

    def pre_save(self):
        self.object.modifie_par = self.request.user
        self.old = ActiviteRisque.objects.get(pk=self.object.pk)
        logger.info("Saving '%s'" % str(self.object))

    def post_save(self):
        logger.info("'%s' Saved successfully" % str(self.object))
        if 'type_de_risque' in get_changes_between_2_objects(self.old, self.object):
            self.object.issue_notification('change_risk_type', actor=self.request.user, target=self.object)


class DeleteActiviterisqueView(PermissionRequiredMixin, AjaxDeleteView):
    permission_required = 'risk_register.delete_activiterisque'
    model = ActiviteRisque
    pk_url_kwarg = 'activiterisque'
    template_name = 'risk_register/confirmer_suppression_activiterisque.html'
    context_object_name = 'activiterisque'

    def post_delete(self):
        logger.info("'%s' successfully deleted" % str(self.object))
        self.object.issue_notification('delete', actor=self.request.user, target=self.object)


class AddControlMixin(AjaxCreateView):
    form_class = AddControleForm


class AddProcessusrisqueControleView(PermissionRequiredMixin, AddControlMixin):
    permission_required = 'risk_register.add_control_process_risk'

    def get_permission_object(self):
        return get_object_or_404(ProcessusRisque, pk=self.kwargs['processusrisque'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['processusrisque'] = get_object_or_404(ProcessusRisque, pk=self.kwargs['processusrisque'])
        return kwargs

    def pre_save(self):
        self.object.cree_par = self.request.user
        self.object.content_object = get_object_or_404(ProcessusRisque, pk=self.kwargs['processusrisque'])
        logger.info("Saving '%s'" % str(self.object))

    def post_save(self):
        logger.info("'%s' Saved successfully" % str(self.object))
        self.object.issue_notification('create', actor=self.request.user, target=self.object)


class AddActiviterisqueControle(PermissionRequiredMixin, AddControlMixin):
    permission_required = 'risk_register.add_control_activity_risk'

    def get_permission_object(self):
        return get_object_or_404(ActiviteRisque, pk=self.kwargs['activiterisque'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['activiterisque'] = get_object_or_404(ActiviteRisque, pk=self.kwargs['activiterisque'])
        return kwargs

    def pre_save(self):
        self.object.cree_par = self.request.user
        self.object.content_object = get_object_or_404(ActiviteRisque, pk=self.kwargs['activiterisque'])
        logger.info("Saving '%s'" % str(self.object))

    def post_save(self):
        logger.info("'%s' Saved successfully" % str(self.object))
        self.object.issue_notification('create', actor=self.request.user, target=self.object)


class EditRiskControl(PermissionRequiredMixin, AjaxUpdateView):
    permission_required = 'risk_register.change_controle'
    model = Controle
    form_class = EditControleForm
    pk_url_kwarg = 'controle'

    def pre_save(self):
        self.object.modifie_par = self.request.user


class DeleteRiskControl(PermissionRequiredMixin, AjaxDeleteView):
    permission_required = 'risk_register.delete_controle'
    model = Controle
    pk_url_kwarg = 'controle'
    context_object_name = 'controle'
    template_name = 'risk_register/confirmer_suppression_controle.html'

    def post_delete(self):
        logger.info("'%s' successfully deleted" % str(self.object))


class AssignerControleView(PermissionRequiredMixin, AjaxUpdateView):
    permission_required = 'risk_register.assign_control'
    model = Controle
    form_class = AssignControlform
    pk_url_kwarg = 'controle'

    def pre_save(self):
        self.object.modifie_par = self.request.user
        logger.info("Assigning '%s' to %s" % (str(self.object), self.object.assigne_a.get_full_name()))

    def post_save(self):
        logger.info("'%s' successfully assigned to %s" % (str(self.object), self.object.assigne_a.get_full_name()))
        self.object.issue_notification('assign', actor=self.request.user, target=self.object)


class SetSeuilProcessusrisqueView(PermissionRequiredMixin, AjaxCreateView):
    permission_required = 'risk_register.set_seuil_process_risk'
    form_class = CritereRisqueForm
    pk_url_kwarg = 'processusrisque'

    def get_permission_object(self):
        return get_object_or_404(ProcessusRisque, pk=self.kwargs['processusrisque'])

    def pre_save(self):
        self.object.evalue_par = self.request.user
        self.object.modifie_par = self.request.user

    def post_save(self):
        processusrisque = get_object_or_404(ProcessusRisque, pk=self.kwargs['processusrisque'])
        if processusrisque.criterisation:
            processusrisque.criterisation.delete()
        processusrisque.criterisation = self.object
        processusrisque.save()
        processusrisque.issue_notification('set_seuil', actor=self.request.user, target=processusrisque)


class ProcessusrisqueEstimationView(PermissionRequiredMixin, AjaxCreateView):
    permission_required = 'risk_register.estimate_process_risk'
    form_class = EstimationRisqueForm
    pk_url_kwarg = 'processusrisque'

    def get_permission_object(self):
        return get_object_or_404(ProcessusRisque, pk=self.kwargs['processusrisque'])

    def form_valid(self, form):
        print(form.data)
        day = form.data.get('date_revue_day')
        month = form.data.get('date_revue_month')
        year = form.data.get('date_revue_year')
        self.date_revue = from_current_timezone(datetime.datetime(year=int(year), month=int(month), day=int(day)))
        return super().form_valid(form)

    def pre_save(self):
        print(self.object)
        self.object.evalue_par = self.request.user

    def post_save(self):
        processusrisque = get_object_or_404(ProcessusRisque, pk=self.kwargs['processusrisque'])
        processusrisque.estimations.create(
            date_revue=self.date_revue,
            criterisation=self.object,
        )
        self.object.issue_notification('create', actor=self.request.user, target=self.object)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['processusrisque'] = get_object_or_404(ProcessusRisque, pk=self.kwargs['processusrisque'])
        return kwargs


class SetSeuilActiviterisqueView(PermissionRequiredMixin, AjaxCreateView):
    form_class = CritereRisqueForm
    pk_url_kwarg = 'activiterisque'
    permission_required = 'risk_register.set_seuil_activity_risk'

    def get_permission_object(self):
        return get_object_or_404(ActiviteRisque, pk=self.kwargs['activiterisque'])

    def pre_save(self):
        self.object.evalue_par = self.request.user
        self.object.modifie_par = self.request.user

    def post_save(self):
        activiterisque = get_object_or_404(ActiviteRisque, pk=self.kwargs['activiterisque'])
        if activiterisque.criterisation:
            activiterisque.criterisation.delete()
        activiterisque.criterisation = self.object
        activiterisque.save()
        activiterisque.issue_notification('set_seuil', actor=self.request.user, target=activiterisque)


class ActiviterisqueEstimationView(PermissionRequiredMixin, AjaxCreateView):
    permission_required = 'risk_register.estimate_activity_risk'
    form_class = EstimationRisqueForm
    pk_url_kwarg = 'activiterisque'

    def get_permission_object(self):
        return get_object_or_404(ActiviteRisque, pk=self.kwargs['activiterisque'])

    def form_valid(self, form):
        print(form.data)
        day = form.data.get('date_revue_day')
        month = form.data.get('date_revue_month')
        year = form.data.get('date_revue_year')
        self.date_revue = from_current_timezone(datetime.datetime(year=int(year), month=int(month), day=int(day)))
        return super().form_valid(form)

    def pre_save(self):
        self.object.evalue_par = self.request.user

    def post_save(self):
        activiterisque = get_object_or_404(ActiviteRisque, pk=self.kwargs['activiterisque'])
        activiterisque.estimations.create(
            criterisation=self.object,
            date_revue=self.date_revue
        )
        self.object.issue_notification('create', actor=self.request.user, target=self.object)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['activiterisque'] = get_object_or_404(ActiviteRisque, pk=self.kwargs['activiterisque'])
        return kwargs


class AssignerActiviterisqueView(PermissionRequiredMixin, AjaxUpdateView):
    form_class = AssignActiviterisqueForm
    pk_url_kwarg = 'activiterisque'
    model = ActiviteRisque
    permission_required = 'risk_register.assign_activity_risk'

    def pre_save(self):
        self.object.modifie_par = self.request.user

    def post_save(self):
        self.object.issue_notification('assign', actor=self.request.user, target=self.object)


class AssignerProcessusrisqueView(PermissionRequiredMixin, AjaxUpdateView):
    permission_required = 'risk_register.assign_process_risk'
    form_class = AssignProcessusrisqueForm
    pk_url_kwarg = 'processusrisque'
    model = ProcessusRisque

    def pre_save(self):
        self.object.modifie_par = self.request.user

    def post_save(self):
        self.object.issue_notification('assign', actor=self.request.user, target=self.object)


class SetProcessusrisqueReviewDate(PermissionRequiredMixin, AjaxUpdateView):
    form_class = ChangeProcessusrisqueReviewDateForm
    pk_url_kwarg = 'processusrisque'
    model = ProcessusRisque
    permission_required = 'risk_register.set_review_date_process_risk'

    def pre_save(self):
        self.object.modifie_par = self.request.user


class SetActiviterisqueReviewDate(PermissionRequiredMixin, AjaxUpdateView):
    form_class = ChangeActiviterisqueReviewDateForm
    pk_url_kwarg = 'activiterisque'
    model = ActiviteRisque
    permission_required = 'risk_register.set_review_date_activity_risk'

    def pre_save(self):
        self.object.modifie_par = self.request.user


class SearchRisk(ListView):
    template_name = 'risk_register/search_result.html'
    context_object_name = 'search_result'
    paginate_by = 10

    def get_queryset(self):
        logger.info('Searching')
        qs = SearchQuery(self.request.GET.get('q'))
        if qs:
            rank = SearchRank(F('search_vector'), qs)
            return Risque.objects.filter(search_vector=qs).annotate(rank=rank).order_by('-rank')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query_text'] = self.request.GET.get('q')
        return context


def check_risk_status(request, pk):
    if request.is_ajax():
        data = {}
        try:
            risque = ProcessusRisque.objects.get(pk=pk)
        except ProcessusRisque.DoesNotExist:
            logger.exception('Process not found')
            try:
                risque = ActiviteRisque.objects.get(pk=pk)
            except ActiviteRisque.DoesNotExist as e:
                logger.exception('Activity not found')
                data['error_message'] = _('Aucun risque trouvé')
                data['result'] = 'failure'

            else:
                data['verifie'] = risque.verifie
                data['result'] = 'success'
        else:
            data['verifie'] = risque.verifie
            data['result'] = 'success'

        return JsonResponse(data)


def check_control_status(request, pk):
    if request.is_ajax():
        data = {}
        try:
            controle = Controle.objects.get(pk=pk)
        except Controle.DoesNotExist:
            logger.exception('Control not found')
            data['error_message'] = _('Contrôle inexistant')
            data['result'] = 'failure'
        else:
            data['result'] = 'success'
            data['status_display'] = controle.get_status_display()
            data['control_status'] = controle.status

        return JsonResponse(data)


@permission_required('risk_register.change_controle', fn=objectgetter(Controle, 'pk'))
def change_control_status(request, pk):
    if request.method == 'POST' and request.is_ajax():
        data = {}

        try:
            controle = Controle.objects.get(pk=pk)
        except Controle.DoesNotExist:
            logger.exception('Controle not found')
            data['error_message'] = _('Contrôle inexistant')
            data['result'] = 'failure'
        else:
            if controle.status != request.POST.get('status'):
                data['result'] = 'failure'
                data['error_message'] = _('statut du contrôle désynchronisé.')
            elif controle.status == 'in_progress':
                controle.status = 'completed'
                controle.save()
                controle.issue_notification('complete', actor=request.user, target=controle)
                data['result'] = 'success'
            elif controle.status == 'completed':
                controle.status = 'in_progress'
                controle.save()
                controle.issue_notification('complete', actor=request.user, target=controle)
                data['result'] = 'success'
            else:
                data['error_message'] = _('statut inconnu')
                data['result'] = 'failure'
        return JsonResponse(data)


def get_risk_id(request, pk):
    try:
        return ActiviteRisque.objects.get(pk=pk)
    except ActiviteRisque.DoesNotExist:
        return get_object_or_404(ProcessusRisque, pk=pk)


@permission_required('risk_register.verify_risque', fn=get_risk_id, raise_exception=True)
def change_risk_status(request, pk):
    if request.method == 'POST' and request.is_ajax():
        data = {}
        try:
            risque = ProcessusRisque.objects.get(pk=pk)
        except ProcessusRisque.DoesNotExist:
            logger.exception('Risk not found')
            try:
                risque = ActiviteRisque.objects.get(pk=pk)
            except ActiviteRisque.DoesNotExist:
                logger.exception('Risk not found')
                risque = None
                data['error_message'] = _('Aucun risque trouvé')
                data['result'] = 'failure'
        if risque:
            if risque.verifie != request.POST.get('verifie'):
                data['result'] = 'failure'
                data['error_message'] = _('statut du risque désynchronisé.')
            elif request.POST.get('verifie') == 'pending':
                risque.verifie = 'verified'
                risque.save()
                risque.issue_notification('verify', actor=request.user, target=risque)
                data['result'] = 'success'
            elif request.POST.get('verifie') == 'verified':
                risque.verifie = 'pending'
                risque.save()
                data['result'] = 'success'
            else:
                data['result'] = 'failure'
                data['error_message'] = _('status du risque inconnu')

        return JsonResponse(data)


def manage_change_risk_status(request, pk):
    # cette fonction est un "hack" pour gere l'exception PermissionDenied
    try:
        return change_risk_status(request, pk)
    except PermissionDenied:
        logger.error('Permission denied')
        return JsonResponse({'permission': 'denied'})


@permission_required('risk_register.approve_controle', fn=objectgetter(Controle, 'pk'))
def approve_controle(request, pk):
    if request.method == 'POST' and request.is_ajax():
        data = {}
        try:
            controle = Controle.objects.get(pk=pk)
        except Controle.DoesNotExist:
            logger.exception('Controle not found')
            data['result'] = 'failure'
            data['error_message'] = _('Contrôle inexistant')
        else:
            if str(controle.est_approuve).lower() == request.POST.get('est_approuve'):
                if controle.est_approuve:
                    controle.est_approuve = False
                else:
                    controle.est_approuve = True
                controle.save()
                controle.issue_notification('approve', actor=request.user, target=controle)

                data['result'] = 'success'
            else:
                data['result'] = 'failure'
                data['error_message'] = _('Données du contrôle désynchronisées')
        return JsonResponse(data)


@permission_required('risk_register.validate_controle_completion', fn=objectgetter(Controle, 'pk'))
def validate_controle(request, pk):
    if request.method == 'POST' and request.is_ajax():
        data = {}
        try:
            controle = Controle.objects.get(pk=pk)
        except Controle.DoesNotExist:
            logger.exception('Controle not found')
            data['result'] = 'failure'
            data['error_message'] = _('Contrôle inexistant')
        else:
            if str(controle.est_valide).lower() == request.POST.get('est_valide'):
                if controle.est_valide:
                    controle.est_valide = False
                else:
                    controle.est_valide = True
                controle.save()
                controle.issue_notification('validate', actor=request.user, target=controle)
                data['result'] = 'success'
            else:
                data['result'] = 'failure'
                data['error_message'] = _('Données du contrôle désynchronisées')
        return JsonResponse(data)


def get_controle_est_valide(request, pk):
    if request.is_ajax():
        data = {}
        try:
            controle = Controle.objects.get(pk=pk)
        except Controle.DoesNotExist:
            logger.exception('Controle not found')
            data['result'] = 'failure'
            data['error_message'] = _('Contrôle inexistant')
        else:
            data['result'] = 'success'
            data['checked'] = controle.est_valide
        return JsonResponse(data)


def get_controle_est_approuve(request, pk):
    if request.is_ajax():
        data = {}
        try:
            controle = Controle.objects.get(pk=pk)
        except Controle.DoesNotExist:
            logger.exception('Controle not found')
            data['result'] = 'failure'
            data['error_message'] = _('Contrôle inexistant')
        else:
            data['result'] = 'success'
            data['checked'] = controle.est_approuve
        return JsonResponse(data)
