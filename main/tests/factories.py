import factory
from main.models import Account, User, Currency, Loan


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')

    
class CurrencyFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Currency

    code = factory.Faker('currency_code')
    name = factory.Faker('currency_name')
    symbol = factory.Faker('currency_symbol')


class AccountFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Account

    user = factory.SubFactory(UserFactory)
    name = factory.Faker('bothify', text='????', letters='abcdefghijklmnopqrstuvwxyz')
    balance = factory.Faker('random_int')
    currency = factory.SubFactory(CurrencyFactory)


class LoanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Loan

    user = factory.SubFactory(UserFactory)
    name = factory.Faker('bothify', text='????', letters='abcdefghijklmnopqrstuvwxyz')
    balance = factory.Faker('random_int')
    currency = factory.SubFactory(CurrencyFactory)