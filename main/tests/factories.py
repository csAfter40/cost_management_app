import factory
import factory.fuzzy
from main.models import Account, Category, Transaction, Transfer, User, Currency, Loan
from django.db.models import signals
import string


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
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

    user = factory.SubFactory(UserFactoryNoSignal)
    name = factory.fuzzy.FuzzyText(length=4, chars=string.ascii_lowercase)
    balance = factory.fuzzy.FuzzyDecimal(low=0)
    currency = factory.SubFactory(CurrencyFactory)


class LoanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Loan

    user = factory.SubFactory(UserFactoryNoSignal)
    name = factory.fuzzy.FuzzyText(length=4, chars=string.ascii_lowercase)
    balance = factory.fuzzy.FuzzyDecimal(low=0)
    currency = factory.SubFactory(CurrencyFactory)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    user = factory.SubFactory(UserFactoryNoSignal)
    name = factory.fuzzy.FuzzyText(length=8, chars=string.ascii_lowercase)
    # parent = factory.fuzzy.FuzzyChoice((factory.SubFactory('main.tests.factories.CategoryFactory'), None))
    parent = factory.SubFactory('main.tests.factories.CategoryFactory')
    type = factory.fuzzy.FuzzyChoice(('I', 'E'))


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    account = factory.SubFactory(AccountFactory)
    name = factory.fuzzy.FuzzyText(length=6, chars=string.ascii_lowercase)
    amount = factory.Faker('random_int')
    date = factory.Faker('date')
    category = factory.SubFactory(CategoryFactory, parent__parent=None)
    type = factory.fuzzy.FuzzyChoice(('I', 'E'))


class TransferFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transfer

    user = factory.SubFactory(UserFactoryNoSignal)
    from_transaction = factory.SubFactory(TransactionFactory)
    to_transaction = factory.SubFactory(TransactionFactory)
    date = factory.Faker('date')