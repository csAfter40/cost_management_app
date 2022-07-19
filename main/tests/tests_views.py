from decimal import Decimal
from test_plus.test import TestCase as TestPlusCase
import factory
from django.db.models import signals
from .cbv_test_mixins import  TestCreateViewMixin
from main.models import Account, Loan
from .factories import CurrencyFactory
from django.urls import reverse
from django.db import models


class TestCreateAccountView(TestCreateViewMixin, TestPlusCase):

    def setUp(self) -> None:
        super().setUp()
        self.test_url_pattern = 'main:create_account'
        self.success_url = reverse('main:index')
        self.model = Account
        self.context_list = ('form', )
        self.template_name = 'main/create_account.html'
        currency = CurrencyFactory()
        self.valid_data = [
            {
                'name': 'sample_account',
                'balance': Decimal(12.00),
                'currency': currency.id,
            },
            {
                'name': 'sample_account',
                'balance': Decimal(0.00),
                'currency': currency.id,
            },
            {
                'name': 'sample_account',
                'balance': Decimal(-12.00),
                'currency': currency.id,
            }
        ]
        self.invalid_data = [{
            'name': 'sample_account',
            'balance': 'abc', # balance must be a number so data is invalid.
            'currency': currency.id,
        }]
    # decorator prevents user preferences object creation by signals.
    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def get_user(self):
        return self.make_user()

    def unit_post_success(self, data):
        super().unit_post_success(data)
        assert self.valid_object.user == self.user

class TestCreateLoanView(TestCreateViewMixin, TestPlusCase):
    def setUp(self) -> None:
        super().setUp()
        self.test_url_pattern = 'main:create_loan'
        self.success_url = reverse('main:index')
        self.model = Loan
        self.context_list = ('form', )
        self.template_name = 'main/create_loan.html'
        currency = CurrencyFactory()
        self.valid_data = [
            {
                'name': 'sample_loan',
                'balance': Decimal(12.00),
                'currency': currency.id,
            },
            {
                'name': 'sample_loan',
                'balance': Decimal(-32.00),
                'currency': currency.id,
            },
        ]
        self.invalid_data = [
            {
                'name': 'sample_account',
                'balance': 'abc', # balance must be a number so data is invalid.
                'currency': currency.id,
            }
        ]    
    
    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def get_user(self):
        return self.make_user()

    def unit_post_success(self, data):
        with self.login(self.user):
            response = self.post(self.test_url_pattern, data=data)
        # test response code
        self.response_302(response)
        # test created object
        self.valid_object = self.get_object()
        assert self.valid_object != None
        for key, value in data.items():
            if isinstance(getattr(self.valid_object, key), models.Model):
                assert getattr(self.valid_object, key).id == value
            elif isinstance(getattr(self.valid_object, key), Decimal):
                assert getattr(self.valid_object, key) == -abs(value)
            else:
                assert getattr(self.valid_object, key) == value
        # test success redirect url
        assert self.success_url in response.get('Location')