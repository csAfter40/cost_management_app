from main.models import (
    Rate, User, Currency, Account, Loan, Category, Transaction,
    Transfer, UserPreferences, CreditCard
)
from main.tests.factories import (
    AccountTransactionFactory, LoanTransactionFactory, RateFactory, UserFactoryNoSignal, CurrencyFactory, AccountFactory, 
    LoanFactory, CategoryFactory, TransactionFactory, TransferFactory, UserPreferencesFactory, CreditCardFactory
)
from main.tests.mixins import BaseFactoryTestMixin
from django.test import TestCase


class TestUserFactoryNoSignal(BaseFactoryTestMixin, TestCase):
    model = User
    factory_class = UserFactoryNoSignal


class TestCurrencyFactory(BaseFactoryTestMixin, TestCase):
    model = Currency
    factory_class = CurrencyFactory


class TestAccountFactory(BaseFactoryTestMixin, TestCase):
    model = Account
    factory_class = AccountFactory


class TestLoanFactory(BaseFactoryTestMixin, TestCase):
    model = Loan
    factory_class = LoanFactory


class TestCreditCardFactory(BaseFactoryTestMixin, TestCase):
    model = CreditCard
    factory_class = CreditCardFactory


class TestCategoryFactory(BaseFactoryTestMixin, TestCase):
    model = Category
    factory_class = CategoryFactory

    def setUp(self):
        self.object = CategoryFactory(parent=None)


class TestAccountTransactionFactory(BaseFactoryTestMixin, TestCase):
    model = Transaction
    factory_class = AccountTransactionFactory


class TestLoanTransactionFactory(BaseFactoryTestMixin, TestCase):
    model = Transaction
    factory_class = LoanTransactionFactory


class TestTransferFactoryNoSignal(BaseFactoryTestMixin, TestCase):
    model = Transfer
    factory_class = TransferFactory


class TestUserPreferecesFactory(BaseFactoryTestMixin, TestCase):
    model = UserPreferences
    factory_class = UserPreferencesFactory

class TestRateFactory(BaseFactoryTestMixin, TestCase):
    model = Rate
    factory_class = RateFactory