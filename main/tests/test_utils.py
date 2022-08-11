from abc import get_cache_token
import decimal
from unicodedata import category
from unittest import mock
from unittest.mock import patch
from django.test.testcases import TestCase
from main.utils import (
    create_categories,
    get_account_data,
    get_category_stats,
    get_dates,
    get_loan_data,
    get_latest_transactions,
    get_latest_transfers,
    get_stats,
    is_owner,
    validate_main_category_uniqueness,
    create_user_categories,
    create_user_preferences
)
from main.tests.factories import (
    CategoryFactory,
    CurrencyFactory,
    TransferFactory,
    UserFactory,
    UserFactoryNoSignal,
    AccountFactory,
    TransactionFactory,
    LoanFactory,
)
import datetime
from datetime import timedelta
from main.categories import categories
from main.models import Category, Transaction, Account, User, UserPreferences


class TestUtilityFunctions(TestCase):
    def setUp(self):
        self.user = UserFactoryNoSignal()

    def test_get_latest_transactions(self):
        today = datetime.date.today()
        user_account = AccountFactory(user=self.user)
        TransactionFactory.create_batch(10)
        for i in range(10):
            TransactionFactory.create(
                account=user_account,
                category__is_transfer=False,
                date=(today - timedelta(days=i)),
            )
            TransactionFactory.create(
                account=user_account,
                category__is_transfer=True,
                date=(today - timedelta(days=i)),
            )
        queryset = get_latest_transactions(self.user, 5)
        self.assertEquals(len(queryset), 5)
        for i, object in enumerate(queryset):
            self.assertEquals(object.account.user, self.user)
            self.assertFalse(object.category.is_transfer)
            if i < len(queryset) - 1:
                self.assertGreater(object.date, queryset[i + 1].date)

    def test_get_latest_transfers(self):
        today = datetime.date.today()
        TransferFactory.create_batch(10)
        for i in range(10):
            TransferFactory.create(user=self.user, date=(today - timedelta(days=i)))
        queryset = get_latest_transfers(self.user, 5)
        self.assertEquals(len(queryset), 5)
        for i, object in enumerate(queryset):
            self.assertEquals(object.user, self.user)
            if i < len(queryset) - 1:
                self.assertGreater(object.date, queryset[i + 1].date)

    def test_create_categories(self):
        create_categories(categories, self.user)
        qs = Category.objects.all()
        self.assertEquals(
            len(categories), qs.filter(parent=None, user=self.user).count()
        )
        for key, value in categories.items():
            if value["children"]:
                self.assertTrue(
                    Category.objects.filter(user=self.user, parent__name=key).exists()
                )

    def test_get_account_data(self):
        accounts = AccountFactory.create_batch(5)
        user_accounts = AccountFactory.create_batch(5, user=self.user)
        data = get_account_data(self.user)
        self.assertEquals(len(data), 5)

    def test_get_loan_data(self):
        loans = AccountFactory.create_batch(5)
        user_loans = LoanFactory.create_batch(5, user=self.user)
        data = get_loan_data(self.user)
        self.assertEquals(len(data), 5)

    def test_validate_main_category_uniqueness(self):
        CategoryFactory(name="duplicate_name", user=self.user, type="E", parent=None)
        self.assertTrue(
            validate_main_category_uniqueness(
                name="unique_name", user=self.user, type="E"
            )
        )
        self.assertFalse(
            validate_main_category_uniqueness(
                name="duplicate_name", user=self.user, type="E"
            )
        )

    def test_get_dates(self):
        context_list = ("today", "week_start", "month_start", "year_start")
        dates = get_dates()
        for date in context_list:
            self.assertIn(date, dates)
        self.assertEquals(dates["today"], datetime.date.today())

    def test_get_stats(self):
        TransactionFactory(type='E', amount=1.00)
        TransactionFactory(type='E', amount=2.00)
        TransactionFactory(type='I', amount=3.00)
        TransactionFactory(type='I', amount=4.00)
        balance = decimal.Decimal(14.00)
        diff = 4.00
        rate = '40.00%'
        stats = get_stats(Transaction.objects.all(), balance)
        self.assertIn('rate', stats)
        self.assertIn('diff', stats)
        self.assertEquals(stats['rate'], rate)
        self.assertEquals(stats['diff'], diff)

    def test_is_owner(self):
        account = AccountFactory(user=self.user)
        self.assertTrue(is_owner(self.user, Account, account.id))

    def test_get_category_stats(self):
        parent_category = CategoryFactory(user=self.user, parent=None)
        categories = CategoryFactory.create_batch(5, user=self.user, parent=parent_category, type='E')
        subcategory = CategoryFactory(user=self.user, parent=categories[0], type='E')
        account = AccountFactory(user=self.user)
        for category in categories[:-1]:
            TransactionFactory(account=account, amount=1, category=category)
        TransactionFactory(account=account, amount=1, category=subcategory)
        qs = Transaction.objects.all()
        category_stats = get_category_stats(qs, 'E', parent_category, self.user)
        self.assertEquals(len(category_stats), 4)
        amount_sum = 0
        for key, value in category_stats.items():
            amount_sum += value['sum']
        self.assertEquals(amount_sum, 5)

    def test_create_user_categories(self):
        CurrencyFactory(id=5)
        UserFactory()
        self.assertTrue(Category.objects.exists())

    def test_create_user_preferences(self):
        CurrencyFactory(id=5)
        UserFactory()
        self.assertTrue(UserPreferences.objects.exists())
