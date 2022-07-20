from decimal import Decimal
import factory
from django.db.models import signals
from .cbv_test_mixins import  TestCreateViewMixin
from main.models import Account, Loan
from .factories import CurrencyFactory, UserFactory
from django.urls import reverse
from django.db import models
from django.test import TestCase
from main import views


class TestCreateAccountView(TestCreateViewMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:create_account')
        cls.success_url = reverse('main:index')
        cls.model = Account
        cls.context_list = ('form', )
        cls.template_name = 'main/create_account.html'
        cls.function = views.CreateAccountView.as_view()

    def setUp(self) -> None:
        super().setUp()
        currency = CurrencyFactory()
        self.valid_data = [
            {
                'name': 'sample_account',
                'balance': Decimal(12.00),
                'currency': currency.id,
            },
            {
                'name': 'sample_account',
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
        return super().get_user()

    def subtest_post_success(self, data):
        response = self.client.post(self.test_url, data=data)
        # test response code
        self.assertRedirects(response, self.success_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        # test created object
        self.valid_object = self.get_object()
        self.assertNotEqual(self.valid_object, None)
        for key, value in data.items():
            if isinstance(getattr(self.valid_object, key), models.Model):
                self.assertEquals(getattr(self.valid_object, key).id, value)
            else:
                self.assertEquals(getattr(self.valid_object, key), value)


class TestCreateLoanView(TestCreateViewMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # cls.test_url_pattern = 'main:create_loan'
        cls.test_url = reverse('main:create_loan')
        cls.success_url = reverse('main:index')
        cls.model = Loan
        cls.context_list = ('form', )
        cls.template_name = 'main/create_loan.html'
        cls.function = views.CreateLoanView.as_view()

    def setUp(self) -> None:
        super().setUp()
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
                'name': 'sample_loan',
                'balance': 'abc', # balance must be a number so data is invalid.
                'currency': currency.id,
            }
        ]    
    
    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def get_user(self):
        return super().get_user()

    def subtest_post_success(self, data):
        response = self.client.post(self.test_url, data=data)
        # test response code
        self.assertRedirects(response, self.success_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        # test created object
        self.valid_object = self.get_object()
        self.assertNotEqual(self.valid_object, None)
        for key, value in data.items():
            if isinstance(getattr(self.valid_object, key), models.Model):
                self.assertEquals(getattr(self.valid_object, key).id, value)
            elif isinstance(getattr(self.valid_object, key), Decimal):
                self.assertEquals(getattr(self.valid_object, key), -abs(value))
            else:
                self.assertEquals(getattr(self.valid_object, key), value)
