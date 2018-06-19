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
        self.pd2 = ProcessDataFactory(nom='Bon de commande')

    def test_str(self):
        self.assertEqual(self.pd2.__str__(), 'Bon de commande')


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
        self.activite1 = ActiviteFactory(
            nom='Prospection téléphonique',
            description='Prospecter les clients par téléphone'
        )

        self.act_risque1 = ActiviteRisquefactory(
            activite=self.activite1,
            risque=factory.SubFactory(RisqueFactory, nom='Risque Pays')
        )
        self.act_risque2 = ActiviteRisquefactory(
            criterisation=None
        )

        self.act_risque3 = ActiviteRisquefactory(
            date_revue=fake.past_datetime(start_date="-60d", tzinfo=utc)
        )

        EstimationFactory(
            content_object=self.act_risque1,
            criterisation=factory.SubFactory(
                CritereDuRisqueFactory, detectabilite=4, severite=5, occurence=4
            ),
            proprietaire=None
        )

    def test_str(self):
        self.assertEqual(self.act_risque1.__str__(), 'Prospection téléphonique/Risque Pays')

    def test_seuil_de_risque(self):
        self.assertEqual(self.act_risque1.seuil_de_risque(), 27)
        self.assertEqual(self.act_risque2.seuil_de_risque(), None)

    def test_clean(self):
        try:
            self.act_risque3.full_clean()
        except ValidationError as e:
            self.assertTrue('date_revue' in e.message_dict)

    def test_facteur_risque(self):
        self.assertEqual(self.act_risque1.facteur_risque(), 80)
        self.assertEqual(self.act_risque2.facteur_risque(), None)

    def test_status_accept(self):
        EstimationFactory(
            content_object=self.act_risque1,
            criterisation=factory.SubFactory(
                CritereDuRisqueFactory, detectabilite=2, severite=3, occurence=4
            )
        )
        self.assertEqual(self.act_risque1.status(), 'acceptable')
        self.assertEqual(self.act_risque2.status(), None)
        self.assertTrue(self.act_risque1.seuil_de_risque() >= self.act_risque1.facteur_risque())

    def test_status_inaccept(self):
        EstimationFactory(
            content_object=self.act_risque1,
            criterisation=factory.SubFactory(
                CritereDuRisqueFactory, detectabilite=4, severite=5, occurence=4
            )
        )

        EstimationFactory(
            content_object=self.act_risque2,
            criterisation=factory.SubFactory(
                CritereDuRisqueFactory, detectabilite=4, severite=5, occurence=4
            )
        )
        self.assertEqual(self.act_risque1.status(), 'inacceptable')
        self.assertEqual(self.act_risque2.status(), None)
        self.assertTrue(self.act_risque1.seuil_de_risque() < self.act_risque1.facteur_risque())

    def test_est_assigne(self):
        EstimationFactory(
            content_object=self.act_risque1,
            criterisation=factory.SubFactory(
                CritereDuRisqueFactory, detectabilite=4, severite=5, occurence=4
            ),
            proprietaire=None
        )
        EstimationFactory(
            content_object=self.act_risque2,
            criterisation=factory.SubFactory(
                CritereDuRisqueFactory, detectabilite=4, severite=5, occurence=4
            )
        )
        self.assertFalse(self.act_risque1.est_assigne())
        self.assertTrue(self.act_risque2.est_assigne())

    def test_get_proprietaire(self):

        EstimationFactory(
            content_object=self.act_risque1,
            criterisation=factory.SubFactory(
                CritereDuRisqueFactory, detectabilite=4, severite=5, occurence=4
            ),
            proprietaire=None
        )

        EstimationFactory(
            content_object=self.act_risque2,
            criterisation=factory.SubFactory(
                CritereDuRisqueFactory, detectabilite=4, severite=5, occurence=4
            )
        )

        self.assertEqual(self.act_risque1.get_proprietaire(), None)
        self.assertNotEqual(self.act_risque2.get_proprietaire(), None)

    def test_est_obsolete(self):
        self.assertTrue(self.act_risque3.est_obsolete)


class TestProcessusRisque(TestCase):
    def setUp(self):
        self.proc_risque = ProcessusRisqueFactory()

    def test_str(self):
        self.assertTrue(self.proc_risque.__str__(), 'Processus-0/Risques Stratégiques-Risque-6')


class TestEstimation(TestCase):
    def setUp(self):
        self.activite1 = ActiviteFactory(
            nom='Prospection téléphonique',
            description='Prospecter les clients par téléphone'
        )

        self.act_risque1 = ActiviteRisquefactory(
            activite=self.activite1,
            risque=factory.SubFactory(RisqueFactory, nom='Risque Pays')
        )

        self.estimation = EstimationFactory(
            content_object=self.act_risque1,
            criterisation=factory.SubFactory(
                CritereDuRisqueFactory, detectabilite=4, severite=5, occurence=4
            )
        )

    def test_str(self):
        self.assertEqual(self.estimation.__str__(), 'Estimation pour: Prospection téléphonique/Risque Pays')


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
