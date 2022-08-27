import decimal
import datetime
from unittest.mock import Mock, MagicMock, patch
from unittest import SkipTest
from django.test.testcases import TestCase
from main.utils import (
    create_categories,
    get_account_data,
    get_category_stats,
    get_dates,
    get_loan_data,
    get_latest_transactions,
    get_latest_transfers,
    get_loan_progress,
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
        super().setUp()
        self.user = UserFactoryNoSignal()

    # def test_get_latest_transactions(self):
    #     today = datetime.date.today()
    #     user_account = AccountFactory(user=self.user)
    #     TransactionFactory.create_batch(10)
    #     for i in range(10):
    #         TransactionFactory.create(
    #             account=user_account,
    #             category__is_transfer=False,
    #             date=(today - timedelta(days=i)),
    #         )
    #         TransactionFactory.create(
    #             account=user_account,
    #             category__is_transfer=True,
    #             date=(today - timedelta(days=i)),
    #         )
    #     queryset = get_latest_transactions(self.user, 5)
    #     self.assertEquals(len(queryset), 5)
    #     for i, object in enumerate(queryset):
    #         self.assertEquals(object.account.user, self.user)
    #         self.assertFalse(object.category.is_transfer)
    #         if i < len(queryset) - 1:
    #             self.assertGreater(object.date, queryset[i + 1].date)
    
    @patch('main.utils.Account')
    @patch('main.utils.Transaction')
    def test_get_latest_transactions_no_db(self, mock_transaction, mock_account):
        user = 'user'
        mock_account.objects.filter.return_value = AccountFactory.build()
        mock_transaction.objects.filter.return_value.exclude.return_value.order_by.return_value = TransactionFactory.build_batch(5)
        transactions = get_latest_transactions(user, 5)
        self.assertTrue(mock_account.called_once)
        self.assertTrue(mock_transaction.called_once)
        self.assertEquals(len(transactions), 5)

    @patch('main.utils.Transfer')
    def test_get_latest_transfers(self, mock):
        user = 'user'
        qty = 5
        mock.objects.filter.return_value.select_related.return_value.order_by.return_value = range(qty)
        transfers = get_latest_transfers(user, qty)
        self.assertTrue(mock.called_once)
        self.assertEquals(len(transfers), qty)


    # def test_get_latest_transfers(self):
    #     today = datetime.date.today()
    #     TransferFactory.create_batch(10)
    #     for i in range(10):
    #         TransferFactory.create(user=self.user, date=(today - timedelta(days=i)))
    #     queryset = get_latest_transfers(self.user, 5)
    #     self.assertEquals(len(queryset), 5)
    #     for i, object in enumerate(queryset):
    #         self.assertEquals(object.user, self.user)
    #         if i < len(queryset) - 1:
    #             self.assertGreater(object.date, queryset[i + 1].date)

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

    # def test_get_account_data(self):
    #     accounts = AccountFactory.create_batch(5)
    #     user_accounts = AccountFactory.create_batch(5, user=self.user)
    #     data = get_account_data(self.user)
    #     self.assertEquals(len(data), 5)

    # def test_get_loan_data(self):
    #     loans = AccountFactory.create_batch(5)
    #     user_loans = LoanFactory.create_batch(5, user=self.user)
    #     data = get_loan_data(self.user)
    #     self.assertEquals(len(data), 5)

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
    
    @patch('main.utils.Category')
    def test_validate_main_category_uniqueness_unit_test(self, mock):
        mock.objects.filter.return_value.exists.return_value = False
        self.assertTrue(validate_main_category_uniqueness('fake_name', 'fake_user', 'fake_type'))
        mock.objects.filter.return_value.exists.assert_called_once()

    @patch('main.utils.date')
    def test_get_dates(self, mock):
        mock.today.return_value = datetime.date(2005, 5, 5)
        mock.side_effect = lambda *args, **kw: datetime.date(*args, **kw)
        context_list = ("today", "week_start", "month_start", "year_start")
        dates = get_dates()
        for date in context_list:
            self.assertIn(date, dates)
        self.assertEquals(dates["today"], datetime.date(2005, 5, 5))
        self.assertEquals(dates["week_start"], datetime.date(2005, 5, 3))
        self.assertEquals(dates["month_start"], datetime.date(2005, 5, 1))
        self.assertEquals(dates["year_start"], datetime.date(2005, 1, 1))

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

    @patch('main.utils.create_categories')    
    def test_create_user_categories_unittest(self, func_mock):
        instance_mock = MagicMock()
        sender_mock = MagicMock()
        create_user_categories(sender_mock, instance_mock, created=False)
        self.assertFalse(func_mock.called)
        create_user_categories(sender_mock, instance_mock, created=True)
        self.assertTrue(func_mock.called)

    def test_create_user_categories(self):
        CurrencyFactory(id=5)
        UserFactory()
        self.assertTrue(Category.objects.exists())

    def test_create_user_preferences(self):
        CurrencyFactory(id=5)
        UserFactory()
        self.assertTrue(UserPreferences.objects.exists())

    @patch('main.utils.Account')
    def test_get_account_data(self, mock):
        qs = AccountFactory.build_batch(5)
        mock.objects.filter.return_value.select_related.return_value = qs
        user = UserFactory.build()
        data = get_account_data(user)
        self.assertTrue(mock.objects.filter.called)
        for obj in qs:
            self.assertEquals(data[obj.id], obj.currency.code)

    @patch('main.utils.Loan')
    def test_get_loan_data(self, mock):
        qs = LoanFactory.build_batch(5)
        mock.objects.filter.return_value.select_related.return_value = qs
        user = UserFactory.build()
        data = get_loan_data(user)
        self.assertTrue(mock.called_once)
        for obj in qs:
            self.assertEquals(data[obj.id], obj.currency.code)

    def test_get_loan_progress(self):
        mock = Mock()
        mock.initial = 10
        mock.balance = 6
        progress = get_loan_progress(mock)
        self.assertEquals(progress, 40)