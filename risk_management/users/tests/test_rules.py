from test_plus import TestCase

from ..rules import is_gm

from .factories import UserFactory, BusinessFactory


class TestPredicate(TestCase):
    def setUp(self):
        self.bu = BusinessFactory(denomination='NH IT Consulting Sarl')
        self.emp = UserFactory(first_name='Abdoul', last_name='Mansour',
                               fonction='general manager', business_unit=self.bu)

    def test_is_gm(self):
        self.assertTrue(is_gm.test(self.emp, self.bu))


class TestPermissions(TestCase):
    def setUp(self):
        self.bu = BusinessFactory(denomination='NH Construction')
        self.emp1 = UserFactory(first_name='Abdoul', last_name='Mansour',
                                fonction='general manager', business_unit=self.bu)
        self.emp2 = UserFactory(first_name='Djoko', last_name='Raoul',
                                fonction='Comptable', business_unit=self.bu)

    def test_has_perm(self):
        self.assertTrue(self.emp1.has_perm('users.add_process_to_bu', self.bu))
        self.assertFalse(self.emp2.has_perm('users.add_process_to_bu', self.bu))
