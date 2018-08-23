from test_plus import TestCase

from ..rules import is_gm

from .factories import UserFactory, BusinessFactory


class TestPredicate(TestCase):
    def setUp(self):
        self.emp = UserFactory(first_name='Abdoul', last_name='Mansour')
        self.bu = BusinessFactory(denomination='NH IT Consulting Sarl',
                                  bu_manager=self.emp)

    def test_is_gm(self):
        self.assertTrue(is_gm.test(self.emp, self.bu))


class TestPermissions(TestCase):
    def setUp(self):
        self.emp1 = UserFactory(first_name='Abdoul', last_name='Mansour',)
        self.emp2 = UserFactory(first_name='Djoko', last_name='Raoul')
        self.bu = BusinessFactory(denomination='NH Construction',
                                  bu_manager=self.emp1)

    def test_has_perm(self):
        self.assertTrue(self.emp1.has_perm('users.add_process_to_bu', self.bu))
        self.assertFalse(self.emp2.has_perm('users.add_process_to_bu', self.bu))
