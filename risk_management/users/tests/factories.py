import factory
import random
from faker import Faker
from ..models import BusinessUnit, User


CIVILITE_CHOICES = ('M.', 'Mme', 'Dr', 'Pr')
faker = Faker('fr_FR')


def generate_phone_number():
    return "(+237) 6%02d%03d%03d" % (random.randint(50, 99), random.randint(0, 999), random.randint(0, 999))


class UserFactory(factory.django.DjangoModelFactory):
    civilite = random.choice(CIVILITE_CHOICES)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    telephone = factory.LazyFunction(generate_phone_number)
    email = factory.LazyAttribute(lambda o: f"{o.first_name.lower()}.{o.last_name.lower()}@noubruholding.com")
    password = factory.PostGenerationMethodCall("set_password", "password")

    class Meta:
        model = User
        django_get_or_create = ("email",)


class BusinessFactory(factory.django.DjangoModelFactory):
    denomination = factory.Sequence(lambda n: f"business unit {n}")
    marche = factory.Faker('text', locale='fr_FR', max_nb_chars=20)
    ville_siege = factory.Faker('city', locale='fr_FR')
    adresse_physique = factory.LazyAttribute(lambda _: faker.street_address())
    telephone = factory.LazyFunction(generate_phone_number)
    bu_manager = factory.SubFactory(UserFactory)
    projet = factory.Faker('pybool')

    class Meta:
        model = BusinessUnit
        django_get_or_create = ('denomination',)

