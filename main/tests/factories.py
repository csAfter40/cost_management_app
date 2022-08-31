import factory
import factory.fuzzy
from main.models import Account, Category, Transaction, Transfer, User, Currency, Loan, UserPreferences
from django.db.models import signals
from django.contrib.contenttypes.models import ContentType
import string


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    # username = factory.Faker('user_name')
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Faker('email')


@factory.django.mute_signals(signals.pre_save, signals.post_save)
class UserFactoryNoSignal(UserFactory):
    pass

    
class CurrencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Currency

    code = factory.Faker('currency_code')
    name = factory.Faker('currency_name')
    symbol = factory.Faker('currency_symbol')


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    id = factory.Sequence(lambda x: x+1)
    user = factory.SubFactory(UserFactoryNoSignal)
    name = factory.fuzzy.FuzzyText(length=4, chars=string.ascii_lowercase)
    balance = factory.fuzzy.FuzzyDecimal(low=0)
    currency = factory.SubFactory(CurrencyFactory)


class LoanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Loan

    id = factory.Sequence(lambda x: x+1)
    user = factory.SubFactory(UserFactoryNoSignal)
    name = factory.fuzzy.FuzzyText(length=4, chars=string.ascii_lowercase)
    balance = factory.fuzzy.FuzzyDecimal(low=0)
    currency = factory.SubFactory(CurrencyFactory)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    user = factory.SubFactory(UserFactoryNoSignal)
    name = factory.fuzzy.FuzzyText(length=8, chars=string.ascii_lowercase)
    parent = factory.SubFactory('main.tests.factories.CategoryFactory')
    type = factory.fuzzy.FuzzyChoice(('I', 'E'))
    is_transfer = factory.fuzzy.FuzzyChoice((True, False, False, False))


class TransactionFactory(factory.django.DjangoModelFactory):
    account = factory.SubFactory(AccountFactory)
    object_id = factory.SelfAttribute('content_object.id')
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object)
    )
    name = factory.fuzzy.FuzzyText(length=6, chars=string.ascii_lowercase)
    amount = factory.Faker('random_int')
    date = factory.Faker('date')
    category = factory.SubFactory(CategoryFactory, parent__parent=None)
    type = factory.fuzzy.FuzzyChoice(('I', 'E'))

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
    currency = factory.SubFactory(CurrencyFactory)