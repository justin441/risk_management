import factory
from test_plus.test import TestCase
from faker import Faker

from .factories import (Processfactory, ProcessDataFactory, ActiviteFactory, ClasseDeRisqueFactory,
                        RisqueFactory, CritereDuRisqueFactory, ActiviteRisquefactory, ProcessusRisqueFactory,
                        EstimationFactory, Controlefactory, utc)


class TestRiskQuery(TestCase):
    def setUp(self):
        self.p_r1 = ProcessusRisqueFactory()
        self.p_r2 = ProcessusRisqueFactory()
        self.p_r3 = ProcessusRisqueFactory()
        self.a_r1 = ActiviteRisquefactory()
        self.a_r2 = ActiviteRisquefactory()
        self.a_r3 = ActiviteRisquefactory()



