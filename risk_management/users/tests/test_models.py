from test_plus.test import TestCase
from .factories import UserFactory, BusinessFactory


class TestUser(TestCase):

    def setUp(self):
        self.user = UserFactory(first_name='Berthe', last_name='Guemnye Kamga')

    def test__str__(self):
        self.assertEqual(
            self.user.__str__(),
            self.user.full_name()
        )
        self.assertEqual(self.user.__str__(),
                         "Berte Guemnye Kamga")

    def test_get_absolute_url(self):
        self.assertEqual(self.user.get_absolute_url(), f"/users/{self.user.username}/")


class TestBusinessUnit(TestCase):
    def setUp(self):
        self.bu = BusinessFactory('Noubru Construction', 'Yaoundé')

    def test__str__(self):
        self.assertEqual(
            self.bu.__str__(),
            'Noubru Construction'
        )
