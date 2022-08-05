from main.models import (
    User, Currency, Account, Loan, Category, Transaction,
    Transfer, UserPreferences,
)
from main.tests.factories import (
    UserFactoryNoSignal, CurrencyFactory, AccountFactory, 
    LoanFactory, CategoryFactory, TransactionFactory, TransferFactory, UserPreferencesFactory
)
from main.tests.mixins import BaseFactoryTestMixin
from django.test import TestCase


class TestUserFactoryNoSignal(BaseFactoryTestMixin, TestCase):
    model = User
    factory_class = UserFactoryNoSignal


class TestCurrencyFactoryNoSignal(BaseFactoryTestMixin, TestCase):
    model = Currency
    factory_class = CurrencyFactory


class TestAccountFactoryNoSignal(BaseFactoryTestMixin, TestCase):
    model = Account
    factory_class = AccountFactory


class TestLoanFactoryNoSignal(BaseFactoryTestMixin, TestCase):
    model = Loan
    factory_class = LoanFactory


class TestCategoryFactoryNoSignal(BaseFactoryTestMixin, TestCase):
    model = Category
    factory_class = CategoryFactory

    def setUp(self):
        self.object = CategoryFactory(parent=None)

class TestTransactionFactoryNoSignal(BaseFactoryTestMixin, TestCase):
    model = Transaction
    factory_class = TransactionFactory


class TestTransferFactoryNoSignal(BaseFactoryTestMixin, TestCase):
    model = Transfer
    factory_class = TransferFactory


class TestUserPreferecesFactory(BaseFactoryTestMixin, TestCase):
    model = UserPreferences
    factory_class = UserPreferencesFactory