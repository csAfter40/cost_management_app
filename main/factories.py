import factory
from .models import User, Currency

class UserFactory(factory.Factory):
    class Meta:
        model = User

    
class CurrencyFactory(factory.Factory):
    class Meta:
        model = Currency
