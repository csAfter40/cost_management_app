from cgi import print_directory
import decimal
import datetime
from locale import currency
from unicodedata import category
from unittest.mock import Mock, MagicMock, patch, call
from django.test.testcases import TestCase
from main.utils import (
    create_categories,
    create_transaction,
    create_transfer,
    get_account_data,
    get_category_stats,
    get_dates,
    get_loan_data,
    get_latest_transactions,
    get_latest_transfers,
    get_loan_payment_transaction_data,
    get_loan_progress,
    get_stats,
    get_payment_stats,
    get_worth_stats,
    get_monthly_asset_balance_change,
    get_monthly_asset_balance,
    get_monthly_currency_balance,
    get_user_currencies,
    get_worth_stats,
    sort_balance_data,
    is_owner,
    validate_main_category_uniqueness,
    convert_str_to_date,
    convert_date_to_str,
    get_next_month,
    fill_missing_monthly_data,
    convert_money,
    get_net_worth_by_currency,
    get_user_net_worths,
    get_currency_account_balances,
    get_accounts_total_balance,
    get_currency_details,
    get_users_grand_total,
    create_user_categories,
    create_user_preferences,
    withdraw_asset_balance,
    handle_transaction_delete,
    edit_asset_balance,
    get_from_transaction,
    get_to_transaction,
)
from main.tests.factories import (
    CategoryFactory,
    CurrencyFactory,
    RateFactory,
    TransactionFactory,
    TransferFactory,
    UserFactory,
    UserFactoryNoSignal,
    AccountFactory,
    AccountTransactionFactory,
    LoanTransactionFactory,
    LoanFactory,
    UserPreferencesFactory,
)
import datetime
from datetime import timedelta
from main.categories import categories
from main.models import Category, Transaction, Account, User, UserPreferences, Transfer
from freezegun import freeze_time


class TestUtilityFunctions(TestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactoryNoSignal()

    @patch('main.utils.Account')
    @patch('main.utils.Transaction')
    def test_get_latest_transactions_no_db(self, mock_transaction, mock_account):
        user = 'user'
        mock_account.objects.filter.return_value.values_list.return_value = [AccountFactory.build().id]
        mock_transaction.objects.filter.return_value.exclude.return_value.order_by.return_value = AccountTransactionFactory.build_batch(5)
        transactions = get_latest_transactions(user, 5)
        self.assertTrue(mock_account.called_once)
        self.assertTrue(mock_transaction.called_once)
        self.assertEquals(len(transactions), 5)

    @patch('main.utils.Transfer')
    def test_get_latest_transfers(self, mock):
        user = 'user'
        qty = 5
        mock.objects.filter.return_value.prefetch_related.return_value.order_by.return_value = range(qty)
        transfers = get_latest_transfers(user, qty)
        self.assertTrue(mock.called_once)
        self.assertEquals(len(transfers), qty)

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
        AccountTransactionFactory(type='E', amount=1.00)
        AccountTransactionFactory(type='I', amount=3.00)
        AccountTransactionFactory(type='E', amount=2.00)
        AccountTransactionFactory(type='I', amount=4.00)
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
            AccountTransactionFactory(content_object=account, amount=1, category=category)
        AccountTransactionFactory(content_object=account, amount=1, category=subcategory)
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

    @freeze_time('2022-05-25')
    def test_get_payment_stats(self):
        loan = LoanFactory(initial=-50000)
        for i in range(1,6):
            LoanTransactionFactory(
                content_object=loan,
                date=datetime.datetime.now()+datetime.timedelta(days=30*i),
                amount=100*i
            )
        data = get_payment_stats(loan)
        self.assertIn('2022-05-25', data)

    def test_get_worth_stats(self):
        response = get_worth_stats(self.user)
        self.assertIsInstance(response, dict)

    def test_get_mothly_asset_balance_change(self):
        account = AccountFactory()
        dates = [
            datetime.date(2022, 2, 10),
            datetime.date(2022, 3, 10),
            datetime.date(2022, 4, 10),
            datetime.date(2022, 4, 15),
        ]
        for date in dates:
            AccountTransactionFactory.create(content_object=account, date=date)
        monthly_totals = get_monthly_asset_balance_change(account)
        self.assertEquals(len(monthly_totals), 3)

    @freeze_time('2022-05-25')
    def test_get_monthly_asset_balance(self):
        account = AccountFactory(balance=decimal.Decimal(10000))
        dates = [
            datetime.date(2022, 6, 10),
            datetime.date(2022, 7, 10),
        ]
        for date in dates:
            AccountTransactionFactory.create(content_object=account, date=date, amount=2000, type='I')
            AccountTransactionFactory.create(content_object=account, date=date, amount=1000, type='E')
        monthly_balances = get_monthly_asset_balance(account)
        expected = {
            '2022-05': 10000,
            '2022-06': 11000,
            '2022-07': 12000,
        }
        self.assertEquals(monthly_balances, expected)

    @freeze_time('2022-05-25')
    def test_get_monthly_currency_balance(self):
        currency = CurrencyFactory()
        currency_account_1 = AccountFactory(user=self.user, balance=decimal.Decimal(10000), currency=currency)
        currency_account_2 = AccountFactory(user=self.user, balance=decimal.Decimal(5000), currency=currency)
        non_currency_account = AccountFactory(user=self.user, balance=decimal.Decimal(20000))
        non_user_account = AccountFactory(currency=currency, balance=decimal.Decimal(20000))
        dates = [
            datetime.date(2022, 6, 10),
            datetime.date(2022, 7, 10),
        ]
        accounts = [currency_account_1, currency_account_2, non_currency_account, non_user_account]
        for date in dates:
            for account in accounts:
                AccountTransactionFactory.create(content_object=account, date=date, amount=2000, type='I')
                AccountTransactionFactory.create(content_object=account, date=date, amount=1000, type='E')
        monthly_balances = get_monthly_currency_balance(user=self.user, currency=currency)
        expected = [
            ('2022-05', 15000),
            ('2022-06', 17000),
            ('2022-07', 19000),
        ]
        self.assertEquals(monthly_balances, expected)
                
    def test_get_user_currencies(self):
        for _ in range(3):
            currency = CurrencyFactory()
            AccountFactory.create_batch(2, user=self.user, currency=currency)
        user_currencies = get_user_currencies(self.user)
        self.assertAlmostEquals(len(user_currencies), 3)

    def test_get_worth_stats(self):
        currencies = set()
        for _ in range(3):
            currency = CurrencyFactory()
            AccountFactory.create_batch(2, user=self.user, currency=currency)
            currencies.add(currency)
        stats = get_worth_stats(user=self.user)
        for currency in currencies:
            self.assertIn(currency, stats)

    def test_sort_balance_data(self):
        data = {'2022-06':5, '2022-01':2, '2022-02':1}
        sorted_data = sort_balance_data(data)
        expected = [('2022-01', 2), ('2022-02', 1), ('2022-06', 5)]
        self.assertEquals(sorted_data, expected)

    def test_convert_srt_to_date(self):
        date = convert_str_to_date('2022-02')
        expected = datetime.datetime(2022,2,1)
        self.assertEquals(date, expected)

    def test_convert_date_to_str(self):
        date = datetime.datetime(2022,2,1)
        str = convert_date_to_str(date)
        self.assertEquals(str, '2022-02')

    def test_get_next_month(self):
        date1 = get_next_month('2022-02')
        date2 = get_next_month('2022-12')
        self.assertEquals(date1,'2022-03')
        self.assertEquals(date2,'2023-01')

    def test_fill_missing_monthly_data(self):
        data = {'2022-02':1, '2022-01':5, '2022-04':9}
        result = fill_missing_monthly_data(data)
        expected = {'2022-02':1, '2022-01':5, '2022-03':1, '2022-04':9}
        self.assertEquals(result, expected)


    def test_convert_money(self):
        from_currency = CurrencyFactory(code='USD')
        to_currency = CurrencyFactory(code='TRY')
        from_rate = RateFactory(currency=from_currency, rate=1)
        to_rate = RateFactory(currency=to_currency, rate=18)
        result = convert_money(from_currency=from_currency, to_currency=to_currency, amount=100)
        expected = 1800
        self.assertEquals(result, expected)

    def test_get_net_worth_by_currency(self):
        currency = CurrencyFactory()
        user_account1_in_currency = AccountFactory(user=self.user, currency=currency, balance=100)
        user_account2_in_currency = AccountFactory(user=self.user, currency=currency, balance=200)
        user_inactive_account_in_currency = AccountFactory(user=self.user, currency=currency, balance=1000, is_active=False)
        user_account_in_other_currency = AccountFactory(user=self.user, balance=1000)
        non_user_account_in_currency = AccountFactory(currency=currency)
        result = get_net_worth_by_currency(user=self.user, currency=currency)
        expected = 300
        self.assertEquals(result, expected)

    def test_get_user_net_worths(self):
        currency1 = CurrencyFactory()
        currency2 = CurrencyFactory()
        currency1_account1 = AccountFactory(user=self.user, currency=currency1, balance=100)
        currency1_account2 = AccountFactory(user=self.user, currency=currency1, balance=200)
        currency2_account1 = AccountFactory(user=self.user, currency=currency2, balance=300)
        currency2_account2 = AccountFactory(user=self.user, currency=currency2, balance=400)
        result = get_user_net_worths(self.user)
        expected = {currency1: 300, currency2: 700}
        self.assertEquals(result, expected)

    def test_get_currency_account_balances(self):
        currency1 = CurrencyFactory()
        currency2 = CurrencyFactory()
        currency1_account1 = AccountFactory(user=self.user, currency=currency1, balance=100)
        currency1_account2 = AccountFactory(user=self.user, currency=currency1, balance=200)
        currency1_account_inactive = AccountFactory(user=self.user, currency=currency2, balance=300, is_active=False)
        currency2_account2 = AccountFactory(user=self.user, currency=currency2, balance=400)
        result = get_currency_account_balances(self.user, currency1)
        expected = {currency1_account1: 100, currency1_account2: 200}
        self.assertEquals(result, expected)

    def test_get_accounts_total_balance(self):
        data = {'account1': 100, 'account2': 200}
        result = get_accounts_total_balance(data)
        expected = 300
        self.assertEquals(result, expected)

    def test_get_currency_details(self):
        currency1 = CurrencyFactory()
        currency2 = CurrencyFactory()
        user_currency1_account1 = AccountFactory(user=self.user, currency=currency1, balance=100)
        user_currency1_account2 = AccountFactory(user=self.user, currency=currency1, balance=200)
        user_currency2_account1 = AccountFactory(user=self.user, currency=currency2, balance=300)
        user_currency2_account2 = AccountFactory(user=self.user, currency=currency2, balance=400)
        result = get_currency_details(self.user)
        expected = {
            currency1: {
                user_currency1_account1: 100,
                user_currency1_account2: 200,
                'total': 300,
            },
            currency2: {
                user_currency2_account1: 300,
                user_currency2_account2: 400,
                'total': 700,
            },
        }
        self.assertEquals(result, expected)

    def test_get_users_grand_total(self):
        currency1 = CurrencyFactory()
        currency2 = CurrencyFactory()
        user_profile = UserPreferencesFactory(user=self.user, primary_currency = currency1)
        rate1 = RateFactory(currency=currency1, rate=1)
        rate2 = RateFactory(currency=currency2, rate=2)
        user_currency1_account1 = AccountFactory(user=self.user, currency=currency1, balance=100)
        user_currency1_account2 = AccountFactory(user=self.user, currency=currency1, balance=200)
        user_currency2_account1 = AccountFactory(user=self.user, currency=currency2, balance=300)
        user_currency2_account2 = AccountFactory(user=self.user, currency=currency2, balance=400)
        currency_details = {
            currency1: {
                user_currency1_account1: 100,
                user_currency1_account2: 200,
                'total': 300,
            },
            currency2: {
                user_currency2_account1: 300,
                user_currency2_account2: 400,
                'total': 700,
            },
        }
        result = get_users_grand_total(user=self.user, data=currency_details)
        expected = {
            'currency': currency1,
            'total': 650
        }
        self.assertEquals(result, expected)

    def test_withdraw_asset_balance_with_account(self):
        account_transaction = AccountTransactionFactory(type='E')
        account = account_transaction.content_object
        amount = account_transaction.amount
        initial_balance = account.balance
        withdraw_asset_balance(account_transaction)
        account.refresh_from_db()
        final_balance = account.balance
        self.assertEquals(final_balance, initial_balance+amount)
    
    def test_withdraw_asset_balance_with_loan(self):
        loan_transaction = LoanTransactionFactory(type='I')
        loan = loan_transaction.content_object
        amount = loan_transaction.amount
        initial_balance = loan.balance
        withdraw_asset_balance(loan_transaction)
        loan.refresh_from_db()
        final_balance = loan.balance
        self.assertEquals(final_balance, initial_balance-amount)

    @patch('main.utils.withdraw_asset_balance')
    def test_handle_transaction_delete(self, mock):
        transaction = AccountTransactionFactory()
        handle_transaction_delete(transaction)
        mock.assert_called_once()

    @patch('main.utils.withdraw_asset_balance')
    def test_handle_transaction_delete_with_loan_payment(self, mock):
        category = CategoryFactory(name='Pay Loan', is_protected=True, parent=None)
        account_transaction = AccountTransactionFactory(type='E', category=category)
        loan_transaction = LoanTransactionFactory(type='I', category=category)
        transfer = TransferFactory(
            from_transaction = account_transaction,
            to_transaction = loan_transaction,
        )
        handle_transaction_delete(account_transaction)
        self.assertEquals(mock.call_count, 2)

    def test_edit_asset_balance_with_expense_transaction(self):
        account = AccountFactory(balance=20)
        transaction = AccountTransactionFactory(type='E', amount=10, content_object=account)
        edit_asset_balance(transaction)
        account.refresh_from_db()
        self.assertEquals(account.balance, 10)

    def test_edit_asset_balance_with_income_transaction(self):
        account = AccountFactory(balance=20)
        transaction = AccountTransactionFactory(type='I', amount=10, content_object=account)
        edit_asset_balance(transaction)
        account.refresh_from_db()
        self.assertEquals(account.balance, 30)

    @patch('main.utils.edit_asset_balance') 
    def test_create_transaction(self, mock):
        account = AccountFactory()
        category = CategoryFactory(parent=None)
        data = {
            'content_object': account,
            'name': 'test',
            'amount': 10,
            'date': datetime.date(2001,1,1),
            'category': category,
            'type': 'E'
        }
        transaction_object = create_transaction(data)
        self.assertIsNotNone(transaction_object)
        self.assertEquals(transaction_object.name, data['name'])
        mock.assert_called_once()

    @patch('main.utils.create_transaction')
    def test_get_from_transaction(self, mock):
        mock.return_value = 'test value'
        data = {
            'from_account': 'from_account',
            'from_amount': 'from_amount',
            'date': 'date',
        }
        result = get_from_transaction(data, user='1')
        mock.assert_called_once()
        self.assertEquals(result, 'test value')
    
    @patch('main.utils.create_transaction')
    def test_get_to_transaction(self, mock):
        mock.return_value = 'test value'
        data = {
            'to_account': 'to_account',
            'to_amount': 'to_amount',
            'date': 'date',
        }
        result = get_to_transaction(data, user='1')
        mock.assert_called_once()
        self.assertEquals(result, 'test value')

    @patch('main.utils.get_to_transaction')
    @patch('main.utils.get_from_transaction')
    def test_create_transfer(self, from_mock, to_mock):
        transaction = AccountTransactionFactory()
        from_mock.return_value = transaction
        to_mock.return_value = transaction
        data = {'date': datetime.date(2001,1,1)}
        create_transfer(data, self.user)
        from_mock.assert_called_once_with(data, self.user)
        to_mock.assert_called_once_with(data, self.user)
        self.assertTrue(Transfer.objects.exists())

    def test_get_loan_payment_transaction_data_with_account(self):
        account = AccountFactory()
        loan = LoanFactory()
        data = {
            'account': account,
            'loan': loan,
            'amount': 10,
            'date': datetime.date(2001, 1, 1)
        }
        form = Mock()
        form.cleaned_data = data
        user = UserFactoryNoSignal()
        form.user = user
        category = CategoryFactory(user=user, name='Pay Loan', parent=None)
        result = get_loan_payment_transaction_data(form, 'account')
        validation_data = {
            'content_object': account,
            'name': 'Pay Loan',
            'amount': 10,
            'date': datetime.date(2001, 1, 1),
            'category': category,
            'type': 'E'
        }
    
    def test_get_loan_payment_transaction_data_with_loan(self):
        account = AccountFactory()
        loan = LoanFactory()
        data = {
            'account': account,
            'loan': loan,
            'amount': 10,
            'date': datetime.date(2001, 1, 1)
        }
        form = Mock()
        form.cleaned_data = data
        user = UserFactoryNoSignal()
        form.user = user
        category = CategoryFactory(user=user, name='Pay Loan', parent=None)
        result = get_loan_payment_transaction_data(form, 'loan')
        validation_data = {
            'content_object': loan,
            'name': 'Pay Loan',
            'amount': 10,
            'date': datetime.date(2001, 1, 1),
            'category': category,
            'type': 'I'
        }