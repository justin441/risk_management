from test_plus.test import TestCase
from .factories import UserFactory, BusinessFactory

from ..admin import MyUserCreationForm


class TestMyUserCreationForm(TestCase):

    def setUp(self):
        self.user = UserFactory(first_name='Alban', last_name='Brice')

    def test_clean_username_success(self):
        # Instantiate the form with a new username
        form = MyUserCreationForm(
            {
                'email': 'fotuepatrice1@gmail.com',
                'civilite': 'M.',
                'first_name': 'Patrice',
                'last_name': 'Fotue Kamga',
                'fonction': 'Assistant Manager de Projet',
                'telephone': '(+234) 674 228 621',
                'business_unit': BusinessFactory('Cameroon Tobacco Company', 'Yaoundé'),
                'password1': 'JsRocks2018',
                'password2': 'JsRocks2018'
            }
        )
        # Run is_valid() to trigger the validation
        valid = form.is_valid()
        self.assertTrue(valid)

        # Run the actual clean_username method
        username = form.clean_username()
        self.assertEqual("patricefotue", username[:-36])

    def test_clean_username_false(self):
        # Instantiate the form with the same username as self.user
        form = MyUserCreationForm(
            {
                "username": self.user.username,
                "password1": "notalamodespassword",
                "password2": "notalamodespassword",
            }
        )
        # Run is_valid() to trigger the validation, which is going to fail
        # because the username is already taken
        valid = form.is_valid()
        self.assertFalse(valid)

        # The form.errors dict should contain a single error called 'username'
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue("username" in form.errors)
