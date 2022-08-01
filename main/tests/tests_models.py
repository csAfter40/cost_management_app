from main.models import (
    User, Currency, UserPreferences, Account, Loan, Category, Transaction,
    Transfer,
)
from main.tests.factories import (
    UserFactoryNoSignal, CurrencyFactory, AccountFactory, 
    LoanFactory, CategoryFactory, TransactionFactory, TransferFactory
)
from django.test import TestCase
from django.db.utils import IntegrityError

class TestUser(TestCase):
    def test_str(self):
        user = UserFactoryNoSignal()
        self.assertEquals(str(user), user.username)

    def test_unique_username(self):
        with self.assertRaises(IntegrityError):
            user1 = UserFactoryNoSignal(username='testuser')
            user2 = UserFactoryNoSignal(username='testuser')
            self.assertIsNotNone(user1)
            self.assertIsNone(user2)

class TestCurrency(TestCase):
    def test_str(self):
        currency = CurrencyFactory()
        self.assertEquals(str(currency), currency.code)

class TestAccount(TestCase):
    def test_str(self):
        account = AccountFactory()
        self.assertEquals(str(account), account.name)

        
