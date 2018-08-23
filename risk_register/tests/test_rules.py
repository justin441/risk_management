from test_plus import TestCase
from risk_management.users.tests.factories import UserFactory, BusinessFactory
from ..rules import *

from .factories import (Processfactory, ActiviteFactory, ActiviteRisquefactory,
                        ProcessusRisqueFactory, EstimationFactory, Controlefactory)


class TestPredicate(TestCase):
    def setUp(self):
        # Business units
        self.bu_mgr1 = UserFactory()
        self.bu_mgr2 = UserFactory()
        self.bu1 = BusinessFactory(denomination='Cameroon Tobacco Company', bu_manager=self.bu_mgr1)
        self.bu2 = BusinessFactory(denomination='Projet Usine Céramique', projet=True, bu_manager=self.bu_mgr2)

        # Processus
        self.proc_mgr1 = UserFactory()
        self.proc_mgr2 = UserFactory()
        self.process1 = Processfactory()
        self.process2 = Processfactory()

        # Activités
        self.act_owner1 = UserFactory()
        self.act_owner2 = UserFactory()
        self.act1 = ActiviteFactory()
        self.act2 = ActiviteFactory()

        # Risques
        self.risk_reporter1 = UserFactory()
        self.risk_reporter2 = UserFactory()
        self.act_risque = ActiviteRisquefactory()

        self.process_risque = ProcessusRisqueFactory()

        # Estimations

        self.risk_owner1 = UserFactory()
        self.risk_owner2 = UserFactory()

        self.estimation1 = EstimationFactory()

        self.estimation2 = EstimationFactory()

        # Contrôles
        self.control_owner1 = UserFactory()
        self.control_owner2 = UserFactory()
        self.control1 = Controlefactory(
            content_object=self.act_risque,
            assigne_a=self.control_owner1,
            cree_par=self.act_owner2
        )
        self.control2 = Controlefactory(
            content_object=self.process_risque,
            assigne_a=self.control_owner2,
            cree_par=self.proc_mgr1
        )

    def test_process_predicates(self):
        self.assertTrue(is_process_manager.test(self.proc_mgr1, self.process1))
        self.assertTrue(is_process_upper_mgt.test(self.bu_mgr1, self.process1))
        self.assertFalse(is_process_manager.test(self.proc_mgr1, self.process2))
        self.assertFalse(is_process_upper_mgt.test(self.bu_mgr2, self.process1))

    def test_act_predicates(self):
        self.assertTrue(is_activity_owner.test(self.act_owner1, self.act1))
        self.assertTrue(is_activity_supervisor.test(self.proc_mgr2, self.act2))
        self.assertTrue(is_activity_upper_mgt.test(self.bu_mgr1, self.act1))
        self.assertFalse(is_activity_owner.test(self.act_owner1, self.act2))
        self.assertFalse(is_activity_supervisor.test(self.proc_mgr2, self.act1))
        self.assertFalse(is_activity_upper_mgt.test(self.bu_mgr2, self.act1))

    def test_act_risque_predicates(self):
        self.assertTrue(is_activity_risk_reporter.test(self.risk_reporter1, self.act_risque))
        self.assertTrue(is_activity_risk_owner.test(self.risk_owner1, self.act_risque))
        self.assertTrue(is_activity_risk_monitor.test(self.act_owner1, self.act_risque))
        self.assertTrue(is_activity_risk_supervisor.test(self.proc_mgr1, self.act_risque))
        self.assertTrue(is_activity_risk_upper_mgt.test(self.bu_mgr1, self.act_risque))

        self.assertFalse(is_activity_risk_reporter.test(self.risk_reporter2, self.act_risque))
        self.assertFalse(is_activity_risk_owner.test(self.risk_owner2, self.act_risque))
        self.assertFalse(is_activity_risk_monitor.test(self.act_owner2, self.act_risque))
        self.assertFalse(is_activity_risk_supervisor.test(self.proc_mgr2, self.act_risque))
        self.assertFalse(is_activity_risk_upper_mgt.test(self.bu_mgr2, self.act_risque))

    def test_process_risk_predicate(self):
        self.assertTrue(is_process_risk_reporter.test(self.risk_reporter2, self.process_risque))
        self.assertTrue(is_process_risk_owner.test(self.risk_owner2, self.process_risque))
        self.assertTrue(is_process_risk_monitor.test(self.proc_mgr2, self.process_risque))
        self.assertTrue(is_process_risk_upper_mgt.test(self.bu_mgr2, self.process_risque))

        self.assertFalse(is_process_risk_reporter.test(self.risk_reporter1, self.process_risque))
        self.assertFalse(is_process_risk_owner.test(self.risk_owner1, self.process_risque))
        self.assertFalse(is_process_risk_monitor.test(self.proc_mgr1, self.process_risque))
        self.assertFalse(is_process_risk_upper_mgt.test(self.bu_mgr1, self.process_risque))

    def test_estimation_predicates(self):
        self.assertTrue(is_estimation_monitor.test(self.proc_mgr1, self.estimation1))
        self.assertTrue(is_estimation_monitor.test(self.proc_mgr2, self.estimation2))

        self.assertFalse(is_estimation_monitor.test(self.proc_mgr1, self.estimation2))

    def test_controle_predicates(self):
        self.assertTrue(is_controle_creator.test(self.act_owner2, self.control1))
        self.assertTrue(is_controle_creator.test(self.proc_mgr1, self.control2))
        self.assertTrue(is_controle_owner.test(self.control_owner1, self.control1))
        self.assertTrue(is_controle_owner.test(self.control_owner2, self.control2))
        self.assertTrue(is_controle_reviewer.test(self.proc_mgr1, self.control1))
        self.assertTrue(is_controle_reviewer.test(self.proc_mgr2, self.control2))

        self.assertFalse(is_controle_creator.test(self.act_owner1, self.control1))
        self.assertFalse(is_controle_creator.test(self.proc_mgr1, self.control1))
        self.assertFalse(is_controle_owner.test(self.control_owner2, self.control1))
        self.assertFalse(is_controle_owner.test(self.control_owner2, self.control1))
        self.assertFalse(is_controle_reviewer.test(self.proc_mgr1, self.control2))
        self.assertFalse(is_controle_reviewer.test(self.proc_mgr1, self.control2))

    def test_bu_mgr_perms(self):
        """test de permissions du dg de l'entité"""
        # sur les processus
        self.assertTrue(self.bu_mgr1.has_perm('risk_register.change_processus', self.process1))
        self.assertTrue(self.bu_mgr1.has_perm('risk_register.delete_processus', self.process1))
        self.assertTrue(self.bu_mgr1.has_perm('risk_register.add_process_data', self.process1))
        # sur les activités
        self.assertTrue(self.bu_mgr1.has_perm('risk_register.add_activity', self.process1))
        self.assertTrue(self.bu_mgr1.has_perm('risk_register.change_activite', self.act1))
        self.assertTrue(self.bu_mgr1.has_perm('risk_register.delete_activite', self.act1))
        # sur les risques des activités
        self.assertTrue(self.bu_mgr1.has_perm('risk_register.set_seuil_activity_risk', self.act_risque))
        self.assertTrue(self.bu_mgr1.has_perm('risk_register.set_review_date_activity_risk', self.act_risque))
        self.assertTrue(self.bu_mgr1.has_perm('risk_register.add_control_activity_risk', self.act_risque))
        self.assertTrue(self.bu_mgr1.has_perm('risk_register.assign_activity_risk', self.act_risque))
        self.assertTrue(self.bu_mgr1.has_perm('risk_register.estimate_activity_risk', self.act_risque))
        self.assertTrue(self.bu_mgr1.has_perm('risk_register.change_activiterisque', self.act_risque))
        self.assertTrue(self.bu_mgr1.has_perm('risk_register.delete_activiterisque', self.act_risque))
        # sur les risques des processus
        self.assertTrue(self.bu_mgr2.has_perm('risk_register.set_seuil_process_risk', self.process_risque))
        self.assertTrue(self.bu_mgr2.has_perm('risk_register.set_review_date_process_risk', self.process_risque))
        self.assertTrue(self.bu_mgr2.has_perm('risk_register.add_control_process_risk', self.process_risque))
        self.assertTrue(self.bu_mgr2.has_perm('risk_register.assign_process_risk', self.process_risque))
        self.assertTrue(self.bu_mgr2.has_perm('risk_register.change_processusrisque', self.process_risque))
        self.assertTrue(self.bu_mgr2.has_perm('risk_register.delete_processusrisque', self.process_risque))
        self.assertTrue(self.bu_mgr2.has_perm('risk_register.estimate_process_risk', self.process_risque))
        # !-
        self.assertFalse(self.bu_mgr2.has_perm('risk_register.change_processus', self.process1))
        self.assertFalse(self.bu_mgr2.has_perm('risk_register.delete_processus', self.process1))
        self.assertFalse(self.bu_mgr2.has_perm('risk_register.add_process_data', self.process1))
        self.assertFalse(self.bu_mgr2.has_perm('risk_register.add_activity', self.process1))
        self.assertFalse(self.bu_mgr2.has_perm('risk_register.change_activite', self.act1))
        self.assertFalse(self.bu_mgr2.has_perm('risk_register.delete_activite', self.act1))
        self.assertFalse(self.bu_mgr2.has_perm('risk_register.set_seuil_activity_risk', self.act_risque))
        self.assertFalse(self.bu_mgr2.has_perm('risk_register.set_review_date_activity_risk', self.act_risque))
        self.assertFalse(self.bu_mgr2.has_perm('risk_register.add_control_activity_risk', self.act_risque))
        self.assertFalse(self.bu_mgr2.has_perm('risk_register.assign_activity_risk', self.act_risque))
        self.assertFalse(self.bu_mgr2.has_perm('risk_register.estimate_activity_risk', self.act_risque))
        self.assertFalse(self.bu_mgr2.has_perm('risk_register.change_activiterisque', self.act_risque))
        self.assertFalse(self.bu_mgr2.has_perm('risk_register.delete_activiterisque', self.act_risque))
        self.assertFalse(self.bu_mgr1.has_perm('risk_register.set_seuil_process_risk', self.process_risque))
        self.assertFalse(self.bu_mgr1.has_perm('risk_register.set_review_date_process_risk', self.process_risque))
        self.assertFalse(self.bu_mgr1.has_perm('risk_register.add_control_process_risk', self.process_risque))
        self.assertFalse(self.bu_mgr1.has_perm('risk_register.assign_process_risk', self.process_risque))
        self.assertFalse(self.bu_mgr1.has_perm('risk_register.change_processusrisque', self.process_risque))
        self.assertFalse(self.bu_mgr1.has_perm('risk_register.delete_processusrisque', self.process_risque))
        self.assertFalse(self.bu_mgr1.has_perm('risk_register.estimate_process_risk', self.process_risque))
        self.assertFalse(self.bu_mgr1.has_perm('risk_register.complete_control', self.control1))

    def test_proc_mgr_perms(self):
        """test des permissions des managers de processus"""
        # sur les processus
        self.assertTrue(self.proc_mgr2.has_perm('risk_register.add_activity', self.process2))
        self.assertTrue(self.proc_mgr2.has_perm('risk_register.add_process_data', self.process2))
        self.assertFalse(self.proc_mgr1.has_perm('risk_register.add_activity', self.process2))
        self.assertFalse(self.proc_mgr1.has_perm('risk_register.add_process_data', self.process2))
        self.assertFalse(self.proc_mgr1.has_perm('risk_register.change_processus', self.process2))
        self.assertFalse(self.proc_mgr1.has_perm('risk_register.delete_processus', self.process2))
        # sur les activités
        self.assertTrue(self.proc_mgr2.has_perm('risk_register.change_activite', self.act2))
        self.assertTrue(self.proc_mgr2.has_perm('risk_register.delete_activite', self.act2))
        self.assertFalse(self.proc_mgr1.has_perm('risk_register.change_activite', self.act2))
        self.assertFalse(self.proc_mgr2.has_perm('risk_register.delete_activite', self.act1))
        # sur les risques des activités
        self.assertTrue(self.proc_mgr1.has_perm('risk_register.set_seuil_activity_risk', self.act_risque))
        self.assertTrue(self.proc_mgr1.has_perm('risk_register.set_review_date_activity_risk', self.act_risque))
        self.assertTrue(self.proc_mgr1.has_perm('risk_register.add_control_activity_risk', self.act_risque))
        self.assertTrue(self.proc_mgr1.has_perm('risk_register.assign_activity_risk', self.act_risque))
        self.assertTrue(self.proc_mgr1.has_perm('risk_register.estimate_activity_risk', self.act_risque))
        self.assertTrue(self.proc_mgr1.has_perm('risk_register.change_activiterisque', self.act_risque))
        self.assertTrue(self.proc_mgr1.has_perm('risk_register.delete_activiterisque', self.act_risque))
        self.assertFalse(self.proc_mgr2.has_perm('risk_register.set_seuil_activity_risk', self.act_risque))
        self.assertFalse(self.proc_mgr2.has_perm('risk_register.set_review_date_activity_risk', self.act_risque))
        self.assertFalse(self.proc_mgr2.has_perm('risk_register.add_control_activity_risk', self.act_risque))
        self.assertFalse(self.proc_mgr2.has_perm('risk_register.assign_activity_risk', self.act_risque))
        self.assertFalse(self.proc_mgr2.has_perm('risk_register.estimate_activity_risk', self.act_risque))
        self.assertFalse(self.proc_mgr2.has_perm('risk_register.change_activiterisque', self.act_risque))
        self.assertFalse(self.proc_mgr2.has_perm('risk_register.delete_activiterisque', self.act_risque))

        # sur les risques des processus
        self.assertTrue(self.proc_mgr2.has_perm('risk_register.set_seuil_process_risk', self.process_risque))
        self.assertTrue(self.proc_mgr2.has_perm('risk_register.set_review_date_process_risk', self.process_risque))
        self.assertTrue(self.proc_mgr2.has_perm('risk_register.add_control_process_risk', self.process_risque))
        self.assertTrue(self.proc_mgr2.has_perm('risk_register.assign_process_risk', self.process_risque))
        self.assertTrue(self.proc_mgr2.has_perm('risk_register.estimate_process_risk', self.process_risque))
        self.assertTrue(self.proc_mgr2.has_perm('risk_register.set_seuil_process_risk', self.process_risque))
        self.assertTrue(self.proc_mgr2.has_perm('risk_register.change_processusrisque', self.process_risque))
        self.assertTrue(self.proc_mgr2.has_perm('risk_register.delete_processusrisque', self.process_risque))
        self.assertFalse(self.proc_mgr1.has_perm('risk_register.set_seuil_process_risk', self.process_risque))
        self.assertFalse(self.proc_mgr1.has_perm('risk_register.set_review_date_process_risk', self.process_risque))
        self.assertFalse(self.proc_mgr1.has_perm('risk_register.add_control_process_risk', self.process_risque))
        self.assertFalse(self.proc_mgr1.has_perm('risk_register.assign_process_risk', self.process_risque))
        self.assertFalse(self.proc_mgr1.has_perm('risk_register.estimate_process_risk', self.process_risque))
        self.assertFalse(self.proc_mgr1.has_perm('risk_register.set_seuil_process_risk', self.process_risque))
        self.assertFalse(self.proc_mgr1.has_perm('risk_register.change_processusrisque', self.process_risque))
        self.assertFalse(self.proc_mgr1.has_perm('risk_register.delete_processusrisque', self.process_risque))
        # sur les estimations
        self.assertTrue(self.proc_mgr2.has_perm('risk_register.set_estimation_review_date', self.estimation2))
        self.assertFalse(self.proc_mgr2.has_perm('risk_register.set_estimation_review_date', self.estimation1))
        # sur les controles
        self.assertTrue(self.proc_mgr2.has_perm('risk_register.assign_control', self.control2))
        self.assertTrue(self.proc_mgr2.has_perm('risk_register.change_controle', self.control2))
        self.assertTrue(self.proc_mgr2.has_perm('risk_register.delete_controle', self.control2))
        self.assertFalse(self.proc_mgr2.has_perm('risk_register.assign_control', self.control1))
        self.assertFalse(self.proc_mgr2.has_perm('risk_register.change_controle', self.control1))
        self.assertFalse(self.proc_mgr2.has_perm('risk_register.delete_controle', self.control1))
        self.assertFalse(self.proc_mgr1.has_perm('risk_register.complete_control', self.control1))

    def test_act_owner_perms(self):
        self.assertTrue(self.act_owner1.has_perm('risk_register.add_control_activity_risk', self.act_risque))
        self.assertFalse(self.act_owner2.has_perm('risk_register.add_activity', self.process2))
        self.assertFalse(self.act_owner2.has_perm('risk_register.add_process_data', self.process2))
        self.assertFalse(self.act_owner2.has_perm('risk_register.change_processus', self.process2))
        self.assertFalse(self.act_owner2.has_perm('risk_register.delete_processus', self.process2))
        self.assertFalse(self.act_owner2.has_perm('risk_register.change_activite', self.act1))
        self.assertFalse(self.act_owner2.has_perm('risk_register.delete_activite', self.act1))
        self.assertFalse(self.act_owner2.has_perm('risk_register.set_seuil_process_risk', self.process_risque))
        self.assertFalse(self.act_owner2.has_perm('risk_register.set_review_date_process_risk', self.process_risque))
        self.assertFalse(self.act_owner2.has_perm('risk_register.add_control_process_risk', self.process_risque))
        self.assertFalse(self.act_owner2.has_perm('risk_register.assign_process_risk', self.process_risque))
        self.assertFalse(self.act_owner2.has_perm('risk_register.estimate_process_risk', self.process_risque))
        self.assertFalse(self.act_owner2.has_perm('risk_register.change_processusrisque', self.process_risque))
        self.assertFalse(self.act_owner2.has_perm('risk_register.delete_processusrisque', self.process_risque))
        self.assertFalse(self.act_owner1.has_perm('risk_register.set_seuil_activity_risk', self.act_risque))
        self.assertFalse(self.act_owner1.has_perm('risk_register.set_review_date_activity_risk', self.act_risque))
        self.assertFalse(self.act_owner1.has_perm('risk_register.assign_activity_risk', self.act_risque))
        self.assertFalse(self.act_owner1.has_perm('risk_register.estimate_activity_risk', self.act_risque))
        self.assertFalse(self.act_owner1.has_perm('risk_register.set_seuil_activity_risk', self.act_risque))
        self.assertFalse(self.act_owner1.has_perm('risk_register.change_activiterisque', self.act_risque))
        self.assertFalse(self.act_owner1.has_perm('risk_register.delete_activiterisque', self.act_risque))
        self.assertFalse(self.act_owner1.has_perm('risk_register.set_estimation_review_date', self.estimation1))
        self.assertFalse(self.act_owner1.has_perm('risk_register.assign_control', self.control1))
        self.assertFalse(self.act_owner1.has_perm('risk_register.change_controle', self.control1))
        self.assertFalse(self.act_owner1.has_perm('risk_register.delete_controle', self.control1))
        self.assertFalse(self.act_owner1.has_perm('risk_register.complete_control', self.control1))

    def test_risks_owner_perm(self):

        self.assertTrue(self.risk_owner2.has_perm('risk_register.add_control_process_risk', self.process_risque))
        self.assertTrue(self.risk_owner2.has_perm('risk_register.estimate_process_risk', self.process_risque))
        self.assertTrue(self.risk_owner1.has_perm('risk_register.add_control_activity_risk', self.act_risque))
        self.assertTrue(self.risk_owner1.has_perm('risk_register.estimate_activity_risk', self.act_risque))
        self.assertFalse(self.risk_owner2.has_perm('risk_register.estimate_activity_risk', self.act_risque))
        self.assertFalse(self.risk_owner2.has_perm('risk_register.add_control_activity_risk', self.act_risque))
        self.assertFalse(self.risk_owner1.has_perm('risk_register.set_seuil_activity_risk', self.act_risque))
        self.assertFalse(self.risk_owner1.has_perm('risk_register.set_review_date_activity_risk', self.act_risque))
        self.assertFalse(self.risk_owner1.has_perm('risk_register.assign_activity_risk', self.act_risque))
        self.assertFalse(self.risk_owner1.has_perm('risk_register.change_activiterisque', self.act_risque))
        self.assertFalse(self.risk_owner1.has_perm('risk_register.delete_activiterisque', self.act_risque))
        self.assertFalse(self.risk_owner2.has_perm('risk_register.set_seuil_process_risk', self.process_risque))
        self.assertFalse(self.risk_owner2.has_perm('risk_register.set_review_date_process_risk', self.process_risque))
        self.assertFalse(self.risk_owner2.has_perm('risk_register.assign_process_risk', self.process_risque))
        self.assertFalse(self.risk_owner2.has_perm('risk_register.change_processusrisque', self.process_risque))
        self.assertFalse(self.risk_owner2.has_perm('risk_register.delete_processusrisque', self.process_risque))
        self.assertFalse(self.risk_owner1.has_perm('risk_register.assign_control', self.control1))
        self.assertFalse(self.risk_owner1.has_perm('risk_register.change_controle', self.control1))
        self.assertFalse(self.risk_owner1.has_perm('risk_register.delete_controle', self.control1))
        self.assertFalse(self.risk_owner1.has_perm('risk_register.complete_control', self.control1))

    def risk_reporter_perms(self):
        self.assertTrue(self.risk_reporter1.has_perm('risk_register.add_control_activity_risk', self.act_risque))
        self.assertTrue(self.risk_reporter1.has_perm('risk_register.estimate_activity_risk', self.act_risque))
        self.assertTrue(self.risk_reporter1.has_perm('risk_register.change_activiterisque', self.act_risque))
        self.assertTrue(self.risk_reporter2.has_perm('risk_register.add_control_process_risk', self.process_risque))
        self.assertTrue(self.risk_reporter2.has_perm('risk_register.estimate_process_risk', self.process_risque))
        self.assertTrue(self.risk_reporter2.has_perm('risk_register.change_processsusrisque', self.process_risque))
        self.assertFalse(self.risk_reporter2.has_perm('risk_register.add_control_activity_risk', self.act_risque))
        self.assertFalse(self.risk_reporter2.has_perm('risk_register.estimate_activity_risk', self.act_risque))
        self.assertFalse(self.risk_reporter2.has_perm('risk_register.change_activiterisque', self.act_risque))
        self.assertFalse(self.risk_reporter2.has_perm('risk_register.set_seuil_activity_risk', self.act_risque))
        self.assertFalse(self.risk_reporter2.has_perm('risk_register.set_review_date_activity_risk', self.act_risque))
        self.assertFalse(self.risk_reporter2.has_perm('risk_register.assign_activity_risk', self.act_risque))
        self.assertFalse(self.risk_reporter2.has_perm('risk_register.delete_activiterisque', self.act_risque))

    def test_controle_owner_perms(self):
        self.assertTrue(self.control_owner2.has_perm('risk_register.complete_control', self.control2))
        self.assertTrue(self.control_owner1.has_perm('risk_register.complete_control', self.control1))
        self.assertFalse(self.control_owner2.has_perm('risk_register.complete_control', self.control1))
        self.assertFalse(self.control_owner2.has_perm('risk_register.assign_control', self.control1))
        self.assertFalse(self.control_owner2.has_perm('risk_register.change_controle', self.control1))
        self.assertFalse(self.control_owner2.has_perm('risk_register.delete_controle', self.control1))

    def controle_creator_perm(self):
        self.assertTrue(self.proc_mgr1.has_perm('risk_register.change_controle', self.control2))
        self.assertTrue(self.proc_mgr1.has_perm('risk_register.delete_controle', self.control2))
        self.assertTrue(self.act_owner2.has_perm('risk_register.change_controle', self.control1))
        self.assertTrue(self.act_owner2.has_perm('risk_register.delete_controle', self.control1))
        self.assertFalse(self.proc_mgr1.has_perm('risk_register.assign_control', self.control2))
        self.assertFalse(self.proc_mgr1.has_perm('risk_register.complete_control', self.control2))
        self.assertFalse(self.act_owner2.has_perm('risk_register.assign_controle', self.control1))
        self.assertFalse(self.act_owner2.has_perm('risk_register.complete_controle', self.control1))











