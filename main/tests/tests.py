from decimal import Decimal
from test_plus.test import TestCase as TestPlusCase
import factory
from django.db.models import signals
from .cbv_test_mixins import  TestCreateViewMixin
from main.models import Account
from .factories import CurrencyFactory
from django.urls import reverse


class TestCreateAccountView2(TestCreateViewMixin, TestPlusCase):

    def setUp(self) -> None:
        super().setUp()
        self.test_url_pattern = 'main:create_account'
        self.success_url = reverse('main:index')
        self.model = Account
        self.context_list = ('form', )
        currency = CurrencyFactory()
        self.data = {
            'name': 'sample_account',
            'balance': Decimal(12.00),
            'currency': currency.id,
        }
    # decorator prevents user preferences object creation by signals.
    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def get_user(self):
        return self.make_user()


    
