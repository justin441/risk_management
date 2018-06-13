import random
import factory
from risk_management.users.tests.factories import UserFactory, BusinessFactory

from ..models import Processus, DonneesProcessus


class Processfactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Processus
        django_get_or_create = ('nom',)

    type_processus = random.choice(['PM', 'PO', 'PS'])
    business_unit = factory.SubFactory(BusinessFactory, denomination=random.choice(
        [
         'Cameroon Tobacco Company',
         'NH Construction',
         'NH security',
         'V.O.C.C'
        ]
    ))
    nom = factory.Sequence(lambda n: f'Processus{n}')
    description = factory.Faker('sentences', ext_word_list=None, nb=3)
    proc_manager = factory.SubFactory(UserFactory, civilite='Mme', first_name='Berthe', last_name='Kamga')


class ProcessDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DonneesProcessus
        django_get_or_create = ('nom', )

    nom = factory.Faker('sentence', nb_words=3)
    processus1 = factory.SubFactory(Processfactory, nom="Vente")
    processus2 = factory.SubFactory(Processfactory, nom="Facturation")
