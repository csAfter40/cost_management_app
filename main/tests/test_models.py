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

    def test_unique_together(self):
        user = UserFactoryNoSignal()
        with self.assertRaises(IntegrityError):
            first_account = AccountFactory(user=user, name='duplicate')
            second_account = AccountFactory(user=user, name='duplicate')


class TestLoan(TestCase):
    def test_str(self):
        loan = LoanFactory()
        self.assertEquals(str(loan), loan.name)

    def test_unique_together(self):
        user = UserFactoryNoSignal()
        with self.assertRaises(IntegrityError):
            first_account = LoanFactory(user=user, name='duplicate')
            second_account = LoanFactory(user=user, name='duplicate')


class TestCategory(TestCase):
    def test_str(self):
        category = CategoryFactory(parent=None)
        self.assertEquals(category.name, str(category))

    def test_unique_together(self):
        parent_category = CategoryFactory(parent=None)
        with self.assertRaises(IntegrityError):
            first_category = CategoryFactory(
                parent=parent_category, 
                name='duplicate'
            )
            second_category = CategoryFactory(
                parent=parent_category, 
                name='duplicate'
            ) 

        
class TestTransaction(TestCase):
    def test_str(self):
        transaction = TransactionFactory()
        self.assertEquals(
            str(transaction),
            (f'{transaction.name} - {transaction.amount} from '
                f'{transaction.account}')
        )


class TestTransfer(TestCase):
    def test_str(self):
        transfer = TransferFactory()
        self.assertEquals(
            str(transfer),
            (f'On {transfer.date} from {transfer.from_transaction.account} to '
                f'{transfer.to_transaction.account} '
                f'{transfer.from_transaction.amount}')
        )