import factory
import factory.fuzzy
from main.models import Account, Category, Transaction, Transfer, User, Currency, Loan
from django.db.models import signals
import string

def get_string_faker(length):
    return factory.Faker('bothify', text=length*'?', letters=string.ascii_lowercase)

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
    name = get_string_faker(4)
    balance = factory.Faker('random_int')
    currency = factory.SubFactory(CurrencyFactory)


class LoanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Loan

    user = factory.SubFactory(UserFactoryNoSignal)
    name = get_string_faker(4)
    balance = factory.Faker('random_int')
    currency = factory.SubFactory(CurrencyFactory)


class TransactionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Transaction

    account = factory.SubFactory(AccountFactory)
    name = get_string_faker(6)
    amount = factory.Faker('random_int')
    date = factory.Faker('date')
    category = None
    type = None


class TransferFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transfer

    user = factory.SubFactory(UserFactoryNoSignal)
    from_transaction = factory.SubFactory(TransactionFactory)
    to_transaction = factory.SubFactory(TransactionFactory)
    date = factory.Faker('date')