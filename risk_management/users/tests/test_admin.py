from test_plus.test import TestCase
from .factories import UserFactory, BusinessFactory, PositionFactory

from ..admin import MyUserCreationForm
from ..forms import BusinessUnitAdminForm
from ..models import User


class TestMyUserCreationForm(TestCase):

    def setUp(self):
        self.user = UserFactory(first_name='Alban', last_name='Brice')

    def test_clean_email_success(self):
        # Instantiate the form with a new username
        form = MyUserCreationForm(
            {
                'email': 'fotuepatrice1@gmail.com',
                'civilite': 'M.',
                'first_name': 'Patrice',
                'last_name': 'Fotue Kamga',
                'telephone': '(+234) 674228621',
                'password1': 'JsRocks2018',
                'password2': 'JsRocks2018'
            }
        )
        # Run is_valid() to trigger the validation
        valid = form.is_valid()
        self.assertTrue(valid)

        # run actual clean_email
        self.assertEqual(form.clean_email(), 'fotuepatrice1@gmail.com')

    def test_username_creation(self):
        # verifiy that username was created
        username = self.user.username
        self.assertEqual("albanbrice", username[:-36])

    def test_clean_username_false(self):
        # Instantiate the form with the same email as self.user
        form = MyUserCreationForm(
            {
                'email': self.user.email,
                'civilite': 'M.',
                'first_name': 'Patrice',
                'last_name': 'Fotue Kamga',
                'telephone': '(+234) 674228621',
                'password1': 'JavaRocks2018',
                'password2': 'JavaRocks2018'
            }
        )
        # Run is_valid() to trigger the validation, which is going to fail
        # because the username is already taken
        valid = form.is_valid()
        self.assertFalse(valid)

        # The form.errors dict should contain a single error called 'username'
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue("email" in form.errors)


class TestBusinessUnitAdminForm(TestCase):
    def setUp(self):
        self.bu = BusinessFactory(denomination='Noubru Construction')
        pos1 = PositionFactory(business_unit=self.bu)
        pos2 = PositionFactory(business_unit=self.bu)

    def test_bu_creation(self):
        bu_form1 = BusinessUnitAdminForm(
            {
                'denomination': '3N pharma',
                'raison_sociale': '',
                'sigle': '',
                'marche': 'Distribution de médicaments',
                'ville_siege': 'Yaoundé',
                'adresse_physique': 'Nkolfoulou',
                'telephone': '674589636',
                'site_web': '',


            }
        )

        valid = bu_form1.is_valid()
        self.assertTrue(valid)
        self.assertFalse('bu_manager' in bu_form1.fields)

    def test_bu_change(self):
        bu_form2 = BusinessUnitAdminForm(
            {
                'raison_sociale': '3N Pharma',
                'sigle': '3NP',
                'marche': 'Distribution de médicaments',
                'ville_siege': 'Yaoundé',
                'adresse_physique': 'Nkolfoulou',
                'telephone': '674589636',
                'site_web': 'www.3npharma.com',

            },
            instance=self.bu)
        valid = bu_form2.is_valid()
        # le champs "denomination" n'apparait pas dans le formulaire de modification
        self.assertFalse('denomination' in bu_form2.fields)
        self.assertTrue(valid)
        self.assertSequenceEqual(list(bu_form2.fields['bu_manager'].queryset), list(self.bu.employes.all()))

