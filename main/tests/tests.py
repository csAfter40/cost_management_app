from decimal import Decimal
from test_plus.test import TestCase as TestPlusCase
import factory
from django.db.models import signals

from main.models import Account
from .factories import CurrencyFactory

class TestCreateAccountView(TestPlusCase):
    # decorator prevents user preferences object creation by signals.
    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def get_user(self):
        return self.make_user()

    def test_unauthenticated_access(self):
        self.assertLoginRequired('main:create_account')

    def test_get(self):
        user = self.get_user()
        with self.login(username=user.username):
            self.get_check_200('main:create_account')
        self.assertInContext('form')

    def test_post(self):
        user = self.get_user()
        currency = CurrencyFactory()
        data = {
            'name': 'sample_account',
            'balance': Decimal(12),
            'currency': currency.id
        }
        with self.login(user):
            response = self.post('main:create_account', data=data)
        # test response code
        self.response_302(response)
        # test created object
        account = Account.objects.all().first()
        assert account.name == data['name']
        assert account.user == user
        # test redirect link
        assert self.reverse('main:index') in response.get('Location')
