from django.urls import reverse, resolve

from test_plus.test import TestCase

from .factories import (BusinessFactory,)


class TestBuUrls(TestCase):
    def setUp(self):
        self.bu = BusinessFactory(
            denomination='Cameroon Tobacco Company'
        )

    def test_bu_reverse(self):
        self.assertEqual(reverse('risk_register:detail_business_unit', kwargs={'denomination': self.bu.denomination}),
                         '/risk-register/Cameroon%20Tobacco%20Company/')

    def test_bu_resolve(self):
        self.assertEqual(resolve('/risk-register/Cameroon%20Tobacco%20Company/').view_name,
                         'risk_register:detail_business_unit')
