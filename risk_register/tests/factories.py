import random
import factory
from datetime import timedelta, tzinfo, datetime
from risk_management.users.tests.factories import UserFactory, BusinessFactory

from django.utils.timezone import now

from ..models import (Processus, ProcessData, Activite, ClasseDeRisques, Risque,
                      CritereDuRisque, ActiviteRisque, ProcessusRisque,
                      Estimation, Controle)


class UTC(tzinfo):
    """
    UTC implementation taken from Python's docs.
    """

    def __repr__(self):
        return "<UTC>"

    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return timedelta(0)


utc = UTC()


class Processfactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Processus
        django_get_or_create = ('nom',)

    type_processus = random.choice(['PM', 'PO', 'PS'])
    business_unit = factory.SubFactory(BusinessFactory, denomination='Cameroon Tobacco Company')
    nom = factory.Sequence(lambda n: f'Process-{n}')
    description = factory.Faker('sentence', ext_word_list=None, nb_words=15, variable_nb_words=True)
    proc_manager = factory.SubFactory(UserFactory, civilite='Mme', first_name='Berthe', last_name='Kamga')


class ProcessDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProcessData
        django_get_or_create = ('nom',)

    nom = factory.Faker('sentence', nb_words=3)
    origine = factory.SubFactory(Processfactory)


class ActiviteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Activite
        django_get_or_create = ('nom',)

    class Params:
        bu_type = 'operation'  # ou 'projet'

    nom = factory.Sequence(lambda n: f'activite-{n}')
    description = factory.Faker('sentence', nb_words=25)
    processus = factory.SubFactory(Processfactory, nom='Vente')
    responsable = factory.SubFactory(UserFactory)
    start = factory.LazyAttribute(lambda o: now() if not o.bu_type == 'operation' else datetime(year=now().year,
                                                                                                month=1,
                                                                                                day=1))
    end = factory.LazyAttribute(
        lambda o: o.start + timedelta(days=365 if o.bu_type == 'operation' else random.choice([90, 180, 730, 270]))
    )


class ClasseDeRisqueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClasseDeRisques
        django_get_or_create = ('nom',)

    nom = random.choice(['Risques Stratégiques', 'Risques Géopolitiques', 'Risques Economiques, Risques Financiers',
                         'Risques Opérationnels'])


class RisqueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Risque
        django_get_or_create = ('nom',)

    classe = factory.SubFactory(ClasseDeRisqueFactory)
    nom = factory.LazyAttributeSequence(lambda o, n: f'{o.classe}-Risque-{n}')
    description = factory.Faker('text', max_nb_chars=500)
    cause = factory.Faker('text', max_nb_chars=500)
    consequence = factory.Faker('text', max_nb_chars=500)


class CritereDuRisqueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CritereDuRisque

    detectabilite = random.choice(range(1, 7))
    severite = random.choice(range(1, 7))
    occurence = random.choice(range(1, 7))


class IdentificationRisqueFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    class Params:
        verified = factory.Trait(
            verifie='verified',
            verifie_par=factory.SubFactory(UserFactory, first_name='Justin', last_name='Fotue',
                                           email='fotuejustin441@.gmail.com'),
            verifie_le=now()
        )

    risque = factory.SubFactory(RisqueFactory)
    type_de_risque = random.choice(['O', 'M'])
    date_revue = factory.Faker('date_time_this_year', before_now=False, after_now=True, tzinfo=utc)
    criterisation = factory.SubFactory(CritereDuRisqueFactory, detectabilite=3, severite=3, occurence=3)
    verifie = 'pending'
    verifie_par = None
    verifie_le = None


class ActiviteRisquefactory(IdentificationRisqueFactory):
    class Meta:
        model = ActiviteRisque

    activite = factory.SubFactory(ActiviteFactory)
    soumis_par = factory.SubFactory(UserFactory)
    modifie_par = None


class ProcessusRisqueFactory(IdentificationRisqueFactory):
    class Meta:
        model = ProcessusRisque

    processus = factory.SubFactory(Processfactory)
    soumis_par = factory.SubFactory(UserFactory)
    modifie_par = None


class EstimationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Estimation

    content_object = factory.SubFactory(ActiviteRisquefactory)
    criterisation = factory.SubFactory(CritereDuRisqueFactory)
    proprietaire = factory.SubFactory(UserFactory, first_name='Justin', last_name='Fotue')
    date_revue = factory.Faker('date_time_this_year', after_now=True, before_now=False, tzinfo=utc)


class Controlefactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Controle

    content_object = factory.SubFactory(ActiviteRisquefactory)
    nom = factory.Faker('text', max_nb_chars=200)
    assigne_a = factory.SubFactory(UserFactory)
    start = factory.Faker('date_time_this_year', after_now=True, before_now=False, tzinfo=utc)
    end = factory.LazyAttribute(
        lambda o: o.start + timedelta(days=60)
    )
