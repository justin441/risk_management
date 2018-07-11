from django.urls import reverse, resolve

from test_plus.test import TestCase

from .factories import (BusinessFactory, Processfactory, ActiviteFactory)


class TestBuUrls(TestCase):
    def setUp(self):
        self.bu = BusinessFactory(
            denomination='Cameroon Tobacco Company'
        )

    def test_bu_reverse(self):
        self.assertEqual(reverse('risk_register:detail_business_unit', kwargs={'pk': self.bu.denomination}),
                         '/risk-register/Cameroon%20Tobacco%20Company/')

    def test_bu_resolve(self):
        self.assertEqual(resolve('/risk-register/Cameroon%20Tobacco%20Company/').view_name,
                         'risk_register:detail_business_unit')


class TestProcessUrls(TestCase):
    def setUp(self):
        self.process = Processfactory(
            nom="Vente"
        )

    def test_process_reverse(self):
        self.assertEqual(reverse('risk_register:detail_processus', kwargs={'pk': self.process.code_processus}),
                         '/risk-register/process/%s/' % self.process.code_processus)

    def test_process_resolve(self):
        self.assertEqual(resolve('/risk-register/process/%s/' % self.process.code_processus).view_name,
                         'risk_register:detail_processus')

    def test_create_process_reverse(self):
        self.assertEqual(reverse('risk_register:creer_processus', kwargs={'business_unit': 'Cameroon Tobacco Company'}),
                         '/risk-register/Cameroon%20Tobacco%20Company/create-process/')

    def test_create_process_resolve(self):
        self.assertEqual(resolve('/risk-register/Cameroon%20Tobacco%20Company/create-process/').view_name,
                         'risk_register:creer_processus')

    def test_update_process_resolve(self):
        self.assertEqual(resolve('/risk-register/%s/update-process/' % self.process.pk).view_name,
                         'risk_register:modifier_processus')

    def test_update_process_reverse(self):
        self.assertEqual(reverse('risk_register:modifier_processus', kwargs={'pk': self.process.pk}),
                         '/risk-register/%s/update-process/' % self.process.pk)


class TestActivityUrls(TestCase):
    def setUp(self):
        self.activity = ActiviteFactory()

    def test_activity_reverse(self):
        self.assertEqual(reverse('risk_register:detail_activite', kwargs={'pk': self.activity.code_activite}),
                         '/risk-register/activity/%s/' % self.activity.code_activite)

    def test_activity_resolve(self):
        self.assertEqual(resolve('/risk-register/activity/%s/' % self.activity.code_activite).view_name,
                         'risk_register:detail_activite')
