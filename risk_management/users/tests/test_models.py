from test_plus.test import TestCase
from .factories import UserFactory, BusinessFactory


class TestUser(TestCase):

    def setUp(self):
        self.user = UserFactory(first_name='Berthe', last_name='Guemnye Kamga')

    def test__str__(self):

        self.assertEqual(self.user.__str__(),
                         'Berthe Guemnye Kamga')

    def test_get_absolute_url(self):
        self.assertEqual(self.user.get_absolute_url(), f"/users/{self.user.username}")


class TestBusinessUnit(TestCase):
    def setUp(self):
        self.bu = BusinessFactory(denomination='NH Construction', ville_siege='Yaoundé')

    def test__str__(self):
        self.assertEqual(
            self.bu.__str__(),
            'NH Construction'
        )
