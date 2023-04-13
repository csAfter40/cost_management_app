import factory
import factory.fuzzy
from main.models import Account, Category, Transaction, Transfer, User, Currency, Loan, UserPreferences, Rate, CreditCard
from django.db.models import signals
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
import string
import datetime
from pytz import UTC

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Faker('email')


@factory.django.mute_signals(signals.pre_save, signals.post_save)
class UserFactoryNoSignal(UserFactory):
    pass

    
class RateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rate

    currency = factory.SubFactory('main.tests.factories.CurrencyFactory', rate=None)
    rate = factory.fuzzy.FuzzyDecimal(0, 10, 2)

class CurrencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Currency

    code = factory.Faker('currency_code')
    name = factory.Faker('currency_name')
    symbol = factory.Faker('currency_symbol')
    rate = factory.RelatedFactory(
        RateFactory,
        factory_related_name='currency',
    )


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    id = factory.Sequence(lambda x: x+1)
    user = factory.SubFactory(UserFactoryNoSignal)
    name = factory.fuzzy.FuzzyText(length=4, chars=string.ascii_lowercase)
    balance = factory.fuzzy.FuzzyDecimal(50000)
    currency = factory.SubFactory(CurrencyFactory)
    initial = factory.SelfAttribute('balance')
    is_active = True


class LoanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Loan

    id = factory.Sequence(lambda x: x+1)
    user = factory.SubFactory(UserFactoryNoSignal)
    name = factory.fuzzy.FuzzyText(length=4, chars=string.ascii_lowercase)
    balance = factory.fuzzy.FuzzyDecimal(low=-50000, high=0)
    currency = factory.SubFactory(CurrencyFactory)
    initial = factory.SelfAttribute('balance')
    is_active = True


class CreditCardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CreditCard

    id = factory.Sequence(lambda x: x+1)
    user = factory.SubFactory(UserFactoryNoSignal)
    name = factory.fuzzy.FuzzyText(length=4, chars=string.ascii_lowercase)
    balance = factory.fuzzy.FuzzyDecimal(low=-50000, high=0)
    currency = factory.SubFactory(CurrencyFactory)
    initial = factory.SelfAttribute('balance')
    is_active = True
    payment_day = factory.fuzzy.FuzzyDecimal(low=1, high=31)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    user = factory.SubFactory(UserFactoryNoSignal)
    name = factory.fuzzy.FuzzyText(length=8, chars=string.ascii_lowercase)
    parent = factory.SubFactory('main.tests.factories.CategoryFactory')
    type = 'E'
    is_transfer = False
    is_protected = False


class TransactionFactory(factory.django.DjangoModelFactory):
    object_id = factory.SelfAttribute('content_object.id')
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object)
    )
    name = factory.fuzzy.FuzzyText(length=6, chars=string.ascii_lowercase)
    amount = factory.Faker('random_int')
    date = factory.Faker('date')
    category = factory.SubFactory(CategoryFactory, parent__parent=None)
    type = 'E'
    installments = None
    due_date = None

    class Meta:
        exclude = 'content_object'
        abstract = True


class LoanTransactionFactory(TransactionFactory):
    content_object = factory.SubFactory(LoanFactory)

    class Meta:
        model = Transaction


class AccountTransactionFactory(TransactionFactory):
    content_object = factory.SubFactory(AccountFactory)

    class Meta:
        model = Transaction

class CreditCardTransactionFactory(TransactionFactory):
    content_object = factory.SubFactory(CreditCardFactory)
    installments = factory.fuzzy.FuzzyInteger(2, 32)
    date = factory.fuzzy.FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC))

    class Meta:
        model = Transaction


class TransferFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transfer

    user = factory.SubFactory(UserFactoryNoSignal)
    from_transaction = factory.SubFactory(AccountTransactionFactory, category__is_transfer=True)
    to_transaction = factory.SubFactory(AccountTransactionFactory, category__is_transfer=True)
    date = factory.Faker('date')


class UserPreferencesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserPreferences

    user = factory.SubFactory(UserFactoryNoSignal)
    primary_currency = factory.SubFactory(CurrencyFactory)


class SessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Session
    
    expire_date = factory.fuzzy.FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC))
    session_key = factory.fuzzy.FuzzyText(length=32, chars=string.ascii_lowercase+string.digits)