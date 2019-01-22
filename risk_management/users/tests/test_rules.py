from test_plus import TestCase

from ..rules import is_gm

from .factories import UserFactory, BusinessFactory, PositionFactory


class TestPredicate(TestCase):
    def setUp(self):
        self.emp = UserFactory(first_name='Abdoul', last_name='Mansour')
        self.bu = BusinessFactory(denomination='NH IT Consulting Sarl')
        PositionFactory(employe=self.emp, business_unit=self.bu)
        self.bu.bu_manager = self.emp
        self.bu.save()

    def test_is_gm(self):
        self.assertTrue(is_gm.test(self.emp, self.bu))


class TestPermissions(TestCase):
    def setUp(self):
        self.emp1 = UserFactory(first_name='Abdoul', last_name='Mansour',)
        self.emp2 = UserFactory(first_name='Djoko', last_name='Raoul')
        self.bu = BusinessFactory(denomination='NH Construction')
        PositionFactory(employe=self.emp1, business_unit=self.bu)
        PositionFactory(employe=self.emp2, business_unit=self.bu)
        self.bu.bu_manager = self.emp1
        self.bu.save()

    def test_has_perm(self):
        self.assertTrue(self.emp1.has_perm('users.add_process_to_bu', self.bu))
        self.assertTrue(self.emp1.has_perm('users.add_businessunit', self.bu))
        self.assertFalse(self.emp2.has_perm('users.add_process_to_bu', self.bu))
        self.assertFalse(self.emp2.has_perm('users.add_businessunit', self.bu))
