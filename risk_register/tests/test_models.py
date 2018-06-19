import factory
from test_plus.test import TestCase
from faker import Faker


from django.core.exceptions import ValidationError
from django.utils.timezone import now

from ..models import ProcessData

from .factories import (Processfactory, ProcessDataFactory, ActiviteFactory, ClasseDeRisqueFactory,
                        RisqueFactory, CritereDuRisqueFactory, ActiviteRisquefactory, ProcessusRisqueFactory,
                        EstimationFactory, Controlefactory, utc)

# Create your tests here.
fake = Faker()


class TestProcess(TestCase):

    def setUp(self):
        self.processus1 = Processfactory(nom='Achat')
        self.processus2 = Processfactory(nom='Vente')

    def test__str(self):
        self.assertEqual(self.processus1.__str__(), 'Cameroon Tobacco Campany: Achat')
        self.assertEqual(self.processus2.__str__(), 'Cameroon Tobacco Campany: Vente')


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
        frs1 = self.pd1.provider
        frs2 = self.pd2.provider
        self.assertEqual(frs1.nom, 'Vente')
        self.assertEqual(frs2, 'Fournisseur externe: ')

    def test_clean(self):
        dp = ProcessData(nom='Achat', processus1=None, processus2=None)
        dp1 = ProcessData(nom='Achat', processus1=self.p1, processus2=self.p1)

        try:
            dp.full_clean()
        except ValidationError as e:
            self.assertTrue('processus1' in e.message_dict)
        try:
            dp1.full_clean()
        except ValidationError as e:
            self.assertTrue('processus1' in e.message_dict)


class TestActivite(TestCase):
    def setUp(self):
        self.activite1 = ActiviteFactory(
            nom='Prospection téléphonique',
            description='Prospecter les clients par téléphone'
        )

        self.activite3 = ActiviteFactory(
            start=fake.date_time_between(start_date="+3d", end_date="now", tzinfo=utc),
            end=fake.date_time_between(start_date="-6d", end_date="now", tzinfo=utc)
        )

    def test__str__(self):
        self.assertEqual(self.activite1.__str__(), 'Prospection téléphonique')

    def test_clean(self):
        try:
            self.activite3.full_clean()
        except ValidationError as e:
            self.assertTrue('end' in e.message_dict)


class TestClasseDeRisque(TestCase):
    def setUp(self):
        self.classe = ClasseDeRisqueFactory(nom='Risques Stratégiques')

    def test_str(self):
        self.assertEqual(self.classe.__str__(), 'Risques Stratégiques')


class TestRisque(TestCase):
    def setUp(self):
        self.risque = RisqueFactory(
            description='Risque de déséquilibre structurel de la chaîne de valeur de l\'entreprise'
        )

    def test_str(self):
        self.assertEqual(self.risque.__str__(),
                         'Risque de déséquilibre structurel de la chaîne de valeur de l\'entreprise')


class TestCritereDuRisque(TestCase):
    def setUp(self):
        self.critere1 = CritereDuRisqueFactory(
            detectabilite=5,
            severite=5,
            occurence=5
        )
        self.critere2 = CritereDuRisqueFactory()

    def test_str(self):
        self.assertEqual(self.critere1.__str__(), 'D: 5; S: 5; O: 5')

    def test_valeur(self):
        self.assertEqual(self.critere1.valeur(), 125)
        self.assertLessEqual(self.critere2.valeur(), 216)


class TestActiviteRisque(TestCase):
    def setUp(self):
        self.act_risque1 = ActiviteRisquefactory()
        self.act_risque2 = ActiviteRisquefactory(
            date_revue=fake.past_datetime(start_date="-60d", tzinfo=utc)
        )

    def test_str(self):
        self.assertEqual(self.act_risque1.__str__(), 'activite-8/Risques Stratégiques-Risque-4')
        self.assertEqual(self.act_risque2.__str__(), 'activite-9/Risques Stratégiques-Risque-5')

    def test_seuil_de_risque(self):
        self.assertEqual(self.act_risque1.seuil_de_risque(), 27)

    def test_clean(self):
        try:
            self.act_risque2.full_clean()
        except ValidationError as e:
            self.assertTrue('date_revue' in e.message_dict)


class TestProcessusRisque(TestCase):
    def setUp(self):
        self.proc_risque = ProcessusRisqueFactory()

    def test_str(self):
        self.assertTrue(self.proc_risque.__str__(), 'Processus-0/Risques Stratégiques-Risque-6')


class TestEstimation(TestCase):
    def setUp(self):
        self.estimation = EstimationFactory()
        self.estimation2 = EstimationFactory(
            content_object=ProcessusRisqueFactory(
                processus=factory.SubFactory(Processfactory, nom='Vente')
            )
        )

    def test_str(self):
        self.assertEqual(self.estimation.__str__(), 'Estimation pour: activite-12/Risques Stratégiques-Risque-8')


class TestControle(TestCase):
    def setUp(self):
        self.controle = Controlefactory(nom='Désigner les membres du comité de suivi du risque')
        self.controle2 = Controlefactory(nom='Reduire le nombre de requêtes vers le serveur',
                                         content_object=ProcessusRisqueFactory(
                                             processus=factory.SubFactory(Processfactory, nom='Vente'))
                                         )

    def test_str(self):
        self.assertEqual(self.controle.__str__(), 'Désigner les membres du comité de suivi du risque')

    def test_clean(self):
        self.controle.start = now()
        self.controle.end = fake.past_datetime(start_date='-30d', tzinfo=utc)
        try:
            self.controle.full_clean()
        except ValidationError as e:
            self.assertTrue('end' in e.message_dict)
