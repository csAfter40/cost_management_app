import factory
from main.models import Account, User, Currency


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')

    
class CurrencyFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Currency

    code = 'ABC'
    name = 'some currency'
    symbol = '&'


class AccountFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Account

    user = factory.SubFactory(UserFactory)
    name = factory.Faker('bothify', text='????', letters='abcdefghijklmnopqrstuvwxyz')
    balance = factory.Faker('random_int')
    currency = factory.SubFactory(CurrencyFactory)