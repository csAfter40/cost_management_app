from locale import currency
from main.models import (
    User,
    Currency,
    UserPreferences,
    Account,
    Loan,
    Category,
    Transaction,
    Transfer,
)
from main.tests.factories import (
    UserFactoryNoSignal,
    CurrencyFactory,
    AccountFactory,
    LoanFactory,
    CategoryFactory,
    AccountTransactionFactory,
    LoanTransactionFactory,
    TransferFactory,
    UserPreferencesFactory,
    RateFactory,
    CreditCardFactory
)
from django.test import TestCase
from django.db.utils import IntegrityError


class TestUser(TestCase):
    def test_str(self):
        user = UserFactoryNoSignal()
        self.assertEquals(str(user), user.username)

    def test_unique_username(self):
        with self.assertRaises(IntegrityError):
            user1 = UserFactoryNoSignal(username="testuser")
            user2 = UserFactoryNoSignal(username="testuser")

    def test_primary_currency_property(self):
        user = UserFactoryNoSignal()
        currency = CurrencyFactory()
        UserPreferencesFactory(user=user, primary_currency=currency)
        self.assertEquals(user.primary_currency, currency)


class TestCurrency(TestCase):
    def test_str(self):
        currency = CurrencyFactory()
        self.assertEquals(str(currency), currency.code)


class TestAccount(TestCase):
    def test_str(self):
        account = AccountFactory()
        self.assertEquals(str(account), account.name)

    def test_unique_constraint_success(self):
        user = UserFactoryNoSignal()
        try:
            first_account = AccountFactory(user=user, name="duplicate", is_active=False)
            second_account = AccountFactory(user=user, name="duplicate", is_active=True)
        except IntegrityError as e:
            self.fail('Failed to create objects together')

    def test_unique_constraint_fail(self):
        user = UserFactoryNoSignal()
        with self.assertRaises(IntegrityError):
            first_account = AccountFactory(user=user, name="duplicate", is_active=True)
            second_account = AccountFactory(user=user, name="duplicate", is_active=True)


class TestLoan(TestCase):
    def test_str(self):
        loan = LoanFactory()
        self.assertEquals(str(loan), loan.name)

    def test_unique_together(self):
        user = UserFactoryNoSignal()
        with self.assertRaises(IntegrityError):
            first_account = LoanFactory(user=user, name="duplicate")
            second_account = LoanFactory(user=user, name="duplicate")


class TestCreditCard(TestCase):
    def test_str(self):
        credit_card = CreditCardFactory()
        self.assertEquals(str(credit_card), credit_card.name)

    def test_unique_together(self):
        user = UserFactoryNoSignal()
        with self.assertRaises(IntegrityError):
            first_card = CreditCardFactory(user=user, name="duplicate", is_active=True)
            second_card = CreditCardFactory(user=user, name="duplicate", is_active=True)

    def test_error_not_raised_when_not_active(self):
        try:
            user = UserFactoryNoSignal()
            first_card = CreditCardFactory(user=user, name="duplicate", is_active=True)
            second_card = CreditCardFactory(user=user, name="duplicate", is_active=False)
        except IntegrityError:
            self.fail("Integrity error raised unexpectedly.")

    def test_payment_day_constraint_gt_31(self):
        with self.assertRaises(IntegrityError):
            CreditCardFactory(payment_day=32)

    def test_payment_day_constraint_lt_1(self):
        with self.assertRaises(IntegrityError):
            CreditCardFactory(payment_day=0)

    def valid_payment_day_constraint(self):
        try:
            CreditCardFactory(payment_day=1)
            CreditCardFactory(payment_day=11)
            CreditCardFactory(payment_day=31)
        except IntegrityError:
            self.fail("Integrity error raised unexpectedly.")
            

class TestCategory(TestCase):
    def test_str(self):
        category = CategoryFactory(parent=None)
        self.assertEquals(category.name, str(category))

    def test_unique_together(self):
        parent_category = CategoryFactory(parent=None)
        with self.assertRaises(IntegrityError):
            first_category = CategoryFactory(parent=parent_category, name="duplicate")
            second_category = CategoryFactory(parent=parent_category, name="duplicate")


class TestTransaction(TestCase):
    def setUp(self):
        super().setUp()
        self.object = AccountTransactionFactory()
        self.couple_object = AccountTransactionFactory()
        self.no_transfer_object = AccountTransactionFactory()
        self.transfer = TransferFactory(
            from_transaction = self.object,
            to_transaction = self.couple_object
        )

    def test_str(self):
        self.assertEquals(
            str(self.object),
            (
                f"{self.object.name} - {self.object.amount} on "
                f"{self.object.content_object}"
            ),
        )

    def test_has_transfer_returns_true(self):
        self.assertTrue(self.object.has_transfer())
    
    def test_has_transfer_returns_false(self):
        self.assertFalse(self.no_transfer_object.has_transfer())

    def test_get_couple_transaction(self):
        self.assertEquals(self.object.get_couple_transaction(), self.couple_object)

    def test_get_couple_transaction_returns_none(self):
        self.assertIsNone(self.no_transfer_object.get_couple_transaction())

    def test_save(self):
        positive_amount_transaction = AccountTransactionFactory(amount=10)
        negative_amount_transaction = AccountTransactionFactory(amount=-10)
        self.assertEquals(positive_amount_transaction.amount, 10)
        self.assertEquals(negative_amount_transaction.amount, 10)


class TestTransfer(TestCase):
    def test_str(self):
        transfer = TransferFactory()
        self.assertEquals(
            str(transfer),
            (
                f"On {transfer.date} from {transfer.from_transaction.content_object} to "
                f"{transfer.to_transaction.content_object} "
                f"{transfer.from_transaction.amount}"
            ),
        )


class TestUserPreferences(TestCase):
    def test_str(self):
        user_preferences = UserPreferencesFactory()
        self.assertEquals(str(user_preferences), f"{user_preferences.user} preferences")

class TestRate(TestCase):
    def test_str(self):
        rate = RateFactory()
        self.assertEquals(str(rate), f'{rate.currency} - {rate.rate}')