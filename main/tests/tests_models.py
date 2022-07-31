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
    def setUp(self) -> None:
        self.user = UserFactoryNoSignal()

    def test_factory(self):
        self.assertIsNotNone(self.user)
        self.assertIsInstance(self.user, User)
        self.assertNotEquals(self.user.username, '')
        self.assertNotEquals(self.user.email, '')

    def test_str(self):
        self.assertEquals(str(self.user), self.user.username)

    def test_unique_username(self):
        with self.assertRaises(IntegrityError):
            user1 = UserFactoryNoSignal(username='testuser')
            user2 = UserFactoryNoSignal(username='testuser')
            self.assertIsNotNone(user1)
            self.assertIsNone(user2)

class TestCurrency(TestCase):
    def setUp(self):
        self.currency = CurrencyFactory()

    def test_factory(self):
        self.assertIsNotNone(self.currency)
        self.assertNotEquals(self.currency.code, '')
        self.assertNotEquals(self.currency.name, '')
        self.assertNotEquals(self.currency.symbol, '')
    
    def test_str(self):
        currency = CurrencyFactory(code='TST')
        self.assertEquals(str(currency), 'TST')
