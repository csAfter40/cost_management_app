import factory
from main.models import User, Currency

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    
class CurrencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Currency

    code = 'ABC'
    name = 'some currency'
    symbol = '&'