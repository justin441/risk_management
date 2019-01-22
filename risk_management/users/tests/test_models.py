from test_plus.test import TestCase
from .factories import UserFactory, BusinessFactory, PositionFactory


class TestUser(TestCase):

    def setUp(self):
        self.user = UserFactory(first_name='Berthe', last_name='Guemnye Kamga')

    def test__str__(self):
        self.assertEqual(self.user.__str__(),
                         'Pr Berthe Guemnye Kamga')

    def test_get_absolute_url(self):
        self.assertEqual(self.user.get_absolute_url(), f"/users/{self.user.username}")


class TestBusinessUnit(TestCase):
    def setUp(self):
        self.bu = BusinessFactory(denomination='NH Construction')
        self.employe = UserFactory(first_name='Yannick', last_name='Noubi')

    def test__str__(self):
        self.assertEqual(
            self.bu.__str__(),
            'NH Construction'
        )

    def test_id(self):
        self.assertEqual(self.bu.id, self.bu.denomination)

    def test_get_absolute_url(self):
        self.assertEqual(self.bu.get_absolute_url(), "/risk-register/business-unit/NH%20Construction/")

    def test_get_bu_type(self):
        self.assertEqual(self.bu.get_bu_type(), "business unit")

    def test_get_managers(self):

        su = UserFactory.build()
        su.is_superuser = True
        su.save()
        PositionFactory(employe=self.employe, business_unit=self.bu)
        self.assertTrue(self.employe in self.bu.employes.all())
        self.assertTrue(bool(self.bu.get_managers()))
        self.bu.bu_manager = self.employe
        self.bu.save()
        self.assertTrue(self.employe in self.bu.get_managers())
        self.assertFalse(su in self.bu.get_managers())

    def test_get_risk_managers(self):
        su1 = UserFactory.build()
        su1.is_superuser = True
        su1.save()
        su2 = UserFactory.build()
        su2.is_superuser = True
        su2.save()
        PositionFactory(poste='Risk manager', employe=su1, business_unit=self.bu)
        PositionFactory(employe=su2, business_unit=self.bu)
        self.assertTrue(su1 in self.bu.get_risk_managers())
        self.assertTrue(su2 in self.bu.get_risk_managers())
        self.assertFalse(self.employe in self.bu.get_risk_managers())
