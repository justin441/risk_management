from django.core.exceptions import ValidationError

from test_plus.test import TestCase
from .factories import Processfactory, ProcessDataFactory
from ..models import DonneesProcessus

# Create your tests here.


class TestProcess(TestCase):

    def setUp(self):
        self.processus1 = Processfactory(nom='Achat')
        self.processus2 = Processfactory(nom='Vente')

    def test__str(self):
        self.assertEqual(self.processus1.__str__(), 'Achat')
        self.assertEqual(self.processus2.__str__(), 'Vente')


class TestProcessData(TestCase):
    def setUp(self):
        self.p1 = Processfactory(nom='Vente')
        self.p2 = Processfactory(nom='Facturation')
        self.p3 = Processfactory(nom='livraison')
        self.pd1 = ProcessDataFactory(nom='Bon de commande', processus1=self.p1, processus2=self.p2)
        self.pd2 = ProcessDataFactory(nom='commande', processus1=None, processus2=self.p1)
        self.pd3 = ProcessDataFactory(nom='Bon de livraison', processus1=self.p3, processus2=None)

    def test_client(self):
        client1 = self.pd1.client
        client2 = self.pd3.client

        self.assertEqual(client1.nom, 'Facturation')
        self.assertEqual(client2, 'Client externe')

    def test_fournisseur(self):
        frs1 = self.pd1.fournisseur
        frs2 = self.pd2.fournisseur
        self.assertEqual(frs1.nom, 'Vente')
        self.assertEqual(frs2, 'Fournisseur externe')

    def test_clean(self):
        dp = DonneesProcessus(nom='Achat', processus1=None, processus2=None)

        try:
            dp.full_clean()
        except ValidationError as e:
            self.assertTrue('Process' in e.message_dict)




