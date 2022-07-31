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
        self.assertNotEquals(self.user.username, '')
        self.assertNotEquals(self.user.email, '')

    def test_str(self):
        self.assertEquals(str(self.user), self.user.username)

    def test_has_username(self):
        user = UserFactoryNoSignal(username='testuser')
        self.assertEquals(user.username, 'testuser')

    def test_has_email(self):
        user = UserFactoryNoSignal(email='testuser@example.com')
        self.assertEquals(user.email, 'testuser@example.com')

    def test_unique_username(self):
        with self.assertRaises(IntegrityError):
            user1 = UserFactoryNoSignal(username='testuser')
            user2 = UserFactoryNoSignal(username='testuser')
            self.assertIsNotNone(user1)
            self.assertIsNone(user2)
