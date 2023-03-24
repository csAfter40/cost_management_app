import decimal
import datetime
import factory
from django.db.models import signals
from unittest.mock import Mock, MagicMock, patch
from django.test.testcases import TestCase
from main.utils import (
    create_categories,
    create_transaction,
    create_transfer,
    get_account_data,
    get_account_balance_data,
    get_category_stats,
    get_conversion_rate,
    get_dates,
    get_credit_card_data,
    get_credit_card_balance_data,
    get_sorted_payment_plan,
    convert_payment_plan_dates,
    get_credit_card_payment_plan,
    add_installments_to_payment_plan,
    get_transaction_installment_due_date,
    get_loan_data,
    get_loan_balance_data,
    get_latest_transactions,
    get_latest_transfers,
    get_payment_transaction_data,
    get_loan_progress,
    get_multi_currency_category_detail_stats,
    get_stats,
    get_payment_stats,
    get_worth_stats,
    get_monthly_asset_balance_change,
    get_monthly_asset_balance,
    get_monthly_currency_balance,
    get_user_currencies,
    get_worth_stats,
    handle_asset_delete,
    handle_debt_payment,
    handle_transfer_delete,
    handle_transfer_edit,
    sort_balance_data,
    is_owner,
    validate_main_category_uniqueness,
    convert_str_to_date,
    convert_date_to_str,
    get_next_month,
    get_valid_date,
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
    edit_transaction,
    get_currency_ins_outs,
    get_ins_outs_report,
    get_report_total,
    get_transactions_currencies,
    get_multi_currency_category_stats,
    get_multi_currency_category_json_stats,
    get_multi_currency_main_category_stats,
    get_category_detail_stats,
    convert_category_stats,
    add_category_stats,
    create_guest_user,
    get_session_from_db,
    setup_guest_user,
    create_guest_user_data,
    create_guest_user_accounts,
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
    CreditCardFactory, 
    CreditCardTransactionFactory,
    SessionFactory
)
import datetime
from datetime import timedelta
from pytz import UTC
from main.categories import categories
from main.models import Category, Transaction, Account, User, UserPreferences, Transfer, Currency, GuestUserSession
from freezegun import freeze_time
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session


class TestUtilityFunctions(TestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactoryNoSignal()

    @patch('main.utils.Account')
    @patch('main.utils.CreditCard')
    @patch('main.utils.Transaction')
    def test_get_latest_transactions_no_db(self, mock_transaction, mock_card, mock_account):
        user = 'user'
        mock_account.objects.filter.return_value.values_list.return_value = [AccountFactory.build().id]
        mock_card.objects.filter.return_value.values_list.return_value = [CreditCardFactory.build().id]
        mock_transaction.objects.filter.return_value.exclude.return_value.order_by.return_value = AccountTransactionFactory.build_batch(5)
        transactions = get_latest_transactions(user, 5)
        self.assertTrue(mock_account.called_once)
        self.assertTrue(mock_card.called_once)
        self.assertTrue(mock_transaction.called_once)
        self.assertEquals(len(transactions), 5)

    @patch('main.utils.Transfer')
    def test_get_latest_transfers(self, mock):
        user = 'user'
        qty = 5
        mock.objects.filter.return_value.prefetch_related.return_value.exclude.return_value.order_by.return_value = range(qty)
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
        self.assertEquals(len(category_stats), 5)
        amount_sum = 0
        for key, value in category_stats.items():
            amount_sum += value['sum']
        self.assertEquals(amount_sum, 10)

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

    @patch('main.utils.Account')
    def test_get_account_balance_data(self, mock):
        qs = AccountFactory.build_batch(5)
        mock.objects.filter.return_value = qs
        user = UserFactory.build()
        data = get_account_balance_data(user)
        self.assertTrue(mock.objects.filter.called)
        for obj in qs:
            self.assertEquals(data[obj.id], obj.balance)

    @patch('main.utils.Loan')
    def test_get_loan_data(self, mock):
        qs = LoanFactory.build_batch(5)
        mock.objects.filter.return_value.select_related.return_value = qs
        user = UserFactory.build()
        data = get_loan_data(user)
        self.assertTrue(mock.called_once)
        for obj in qs:
            self.assertEquals(data[obj.id], obj.currency.code)
    
    @patch('main.utils.CreditCard')
    def test_get_credit_card_data(self, mock):
        qs = CreditCardFactory.build_batch(5)
        mock.objects.filter.return_value.select_related.return_value = qs
        user = UserFactory.build()
        data = get_credit_card_data(user)
        self.assertTrue(mock.called_once)
        for obj in qs:
            self.assertEquals(data[obj.id], obj.currency.code)

    @patch('main.utils.Loan')
    def test_get_loan_balance_data(self, mock):
        qs = LoanFactory.build_batch(5)
        mock.objects.filter.return_value = qs
        user = UserFactory.build()
        data = get_loan_balance_data(user)
        self.assertTrue(mock.called_once)
        for obj in qs:
            self.assertEquals(data[obj.id], obj.balance)

    @patch('main.utils.CreditCard')
    def test_get_credit_card_balance_data(self, mock):
        qs = CreditCardFactory.build_batch(5)
        mock.objects.filter.return_value = qs
        user = UserFactory.build()
        data = get_credit_card_balance_data(user)
        self.assertTrue(mock.called_once)
        for obj in qs:
            self.assertEquals(data[obj.id], obj.balance)

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

    def test_get_valid_date(self):
        date1 = get_valid_date(2002, 2, 21)
        date2 = get_valid_date(2002, 2, 31)
        date3 = get_valid_date(2004, 2, 31)
        self.assertEquals(date1, datetime.date(2002, 2, 21))
        self.assertEquals(date2, datetime.date(2002, 2, 28))
        self.assertEquals(date3, datetime.date(2004, 2, 29))

    @patch("main.utils.date")
    def test_fill_missing_monthly_data(self, mock):
        mock.today.return_value = datetime.date(2022, 6, 1)
        data = {'2022-02':1, '2022-01':5, '2022-04':9}
        result = fill_missing_monthly_data(data)
        expected = {'2022-02':1, '2022-01':5, '2022-03':1, '2022-04':9, '2022-05':9, '2022-06':9,}
        self.assertEquals(result, expected)

    def test_get_conversion_rate(self):
        from_currency = CurrencyFactory(code='USD', rate__rate=1)
        to_currency = CurrencyFactory(code='TRY', rate__rate=18)
        result = get_conversion_rate(from_currency=from_currency, to_currency=to_currency)
        expected = 18
        self.assertEquals(result, expected)

    @patch('main.utils.get_conversion_rate')
    def test_convert_money(self, mock):
        mock.return_value = 18
        result = convert_money(from_currency='from_currency', to_currency='to_currency', amount=100)
        expected = 1800
        self.assertEquals(result, expected)
        self.assertTrue(mock.called)

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
        currency1 = CurrencyFactory(rate__rate=1)
        currency2 = CurrencyFactory(rate__rate=2)
        user_profile = UserPreferencesFactory(user=self.user, primary_currency = currency1)
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
            'type': 'E',
            'installments': None,
            'due_date': None
        }
        transaction_object = create_transaction(data)
        self.assertIsNotNone(transaction_object)
        self.assertEquals(transaction_object.name, data['name'])
        mock.assert_called_once()

    @patch('main.utils.get_transaction_installment_due_date')
    def test_create_transaction_with_due_date(self, mock):
        due_date = datetime.datetime(2001, 4, 5, tzinfo=UTC)
        mock.return_value = due_date
        card = CreditCardFactory()
        category = CategoryFactory(parent=None)
        data = {
            'content_object': card,
            'name': 'test',
            'amount': 10,
            'date': datetime.date(2001,1,1),
            'category': category,
            'type': 'E',
            'installments': 4
        }
        transaction_object = create_transaction(data)
        self.assertIsNotNone(transaction_object)
        self.assertEquals(transaction_object.due_date, due_date)
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

    def test_get_payment_transaction_data_with_account(self):
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
        category = CategoryFactory(user=user, name='Pay Debt', parent=None, type='E')
        result = get_payment_transaction_data(form, 'account')
        validation_data = {
            'content_object': account,
            'name': 'Pay Debt',
            'amount': 10,
            'date': datetime.date(2001, 1, 1),
            'category': category,
            'type': 'E'
        }
        self.assertEquals(result, validation_data)
    
    def test_get_payment_transaction_data_with_loan(self):
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
        category = CategoryFactory(user=user, name='Pay Debt', parent=None, type='I')
        result = get_payment_transaction_data(form, 'loan')
        validation_data = {
            'content_object': loan,
            'name': 'Pay Debt',
            'amount': 10,
            'date': datetime.date(2001, 1, 1),
            'category': category,
            'type': 'I'
        }
        self.assertEquals(result, validation_data)
    
    def test_get_payment_transaction_data_with_card(self):
        account = AccountFactory()
        card = CreditCardFactory()
        data = {
            'account': account,
            'card': card,
            'amount': 10,
            'date': datetime.date(2001, 1, 1)
        }
        form = Mock()
        form.cleaned_data = data
        user = UserFactoryNoSignal()
        form.user = user
        category = CategoryFactory(user=user, name='Pay Debt', parent=None, type='I')
        result = get_payment_transaction_data(form, 'card')
        validation_data = {
            'content_object': card,
            'name': 'Pay Debt',
            'amount': 10,
            'date': datetime.date(2001, 1, 1),
            'category': category,
            'type': 'I'
        }
        self.assertEquals(result, validation_data)

    @patch('main.utils.create_transaction')
    @patch('main.utils.get_payment_transaction_data')
    def test_handle_debt_payment_with_loan_asset(self, get_mock, create_mock):
        transaction = AccountTransactionFactory()
        create_mock.return_value = transaction
        form = Mock()
        form.user = UserFactoryNoSignal()
        handle_debt_payment(form, "loan")
        self.assertEquals(create_mock.call_count, 2)
        self.assertEquals(get_mock.call_count, 2)
        self.assertTrue(Transfer.objects.exists())

    @patch('main.utils.create_transaction')
    @patch('main.utils.get_payment_transaction_data')
    def test_handle_debt_payment_with_card_asset(self, get_mock, create_mock):
        transaction = AccountTransactionFactory()
        create_mock.return_value = transaction
        form = Mock()
        form.user = UserFactoryNoSignal()
        handle_debt_payment(form, "card")
        self.assertEquals(create_mock.call_count, 2)
        self.assertEquals(get_mock.call_count, 2)
        self.assertTrue(Transfer.objects.exists())

    @patch('main.utils.create_transaction')
    def test_handle_asset_delete_with_positive_balance(self, mock):
        CategoryFactory(parent=None, user=self.user, type='E', name='Asset Delete')
        asset = AccountFactory(balance=10, user=self.user)
        handle_asset_delete(asset)
        mock.assert_called_once()

    @patch('main.utils.create_transaction')
    def test_handle_asset_delete_with_negative_balance(self, mock):
        CategoryFactory(parent=None, user=self.user, type='I', name='Asset Delete')
        asset = AccountFactory(balance=-10, user=self.user)
        handle_asset_delete(asset)
        mock.assert_called_once()

    @patch('main.utils.create_transaction')
    def test_handle_asset_delete_with_zero_balance(self, mock):
        asset = AccountFactory(balance=0, user=self.user)
        handle_asset_delete(asset)
        mock.assert_not_called()

    @patch('main.utils.handle_transaction_delete')
    def test_handle_transfer_delete(self, mock):
        from_transaction = AccountTransactionFactory()
        transfer = TransferFactory(from_transaction=from_transaction)
        handle_transfer_delete(transfer)
        mock.assert_called_once_with(from_transaction)

    @patch('main.utils.withdraw_asset_balance')
    @patch('main.utils.edit_asset_balance')
    def test_edit_transaction(self,edit_mock, withdraw_mock):
        object = AccountTransactionFactory()
        data = {
            'content_object': AccountFactory(name='new account'),
            'amount': 10,
            'date': datetime.date(2001,1,1)
        }
        edit_transaction(object, data)
        self.assertEquals(object.content_object.name, 'new account')
        self.assertEquals(object.amount, 10)
        self.assertEquals(object.date, datetime.date(2001,1,1))
        withdraw_mock.assert_called_once()
        edit_mock.assert_called_once()

    @patch('main.utils.edit_transaction')
    def test_handle_transfer_edit(self, mock):
        object = TransferFactory(date=datetime.date(1999,1,1))
        data = {
            'from_account': 'from_account',
            'from_amount': 'from_amount',
            'to_account': 'to_account',
            'to_amount': 'to_amount',
            'date': datetime.date(2001,1,1)
        }
        handle_transfer_edit(object, data)
        self.assertEquals(mock.call_count, 2)
        self.assertEquals(object.date, datetime.date(2001,1,1))

    def test_get_currency_ins_outs(self):
        currency = CurrencyFactory()
        account = AccountFactory(currency=currency, user=self.user)
        AccountTransactionFactory(content_object=account, type='E', amount=10)
        AccountTransactionFactory(content_object=account, type='I', amount=20)
        qs = Transaction.objects.all()
        data = get_currency_ins_outs(currency, qs, self.user)
        expected = {
            'currency': currency,
            'expense': 10,
            'income': 20,
            'balance': 10
        }
        self.assertEquals(data, expected)

    @patch('main.utils.Currency.objects.filter')
    @patch('main.utils.get_report_total')
    def test_get_ins_outs_report(self, mock_total, mock_Currency):
        currency1 = Mock()
        currency2 = Mock()
        mock_Currency.return_value.prefetch_related.return_value.annotate.return_value.annotate.return_value = [currency1, currency2]
        mock_total.return_value = 'total'
        get_ins_outs_report('user', 'qs', 'target_currency')
        self.assertTrue(mock_Currency.called)
        self.assertTrue(mock_total.called)

    def test_get_report_total(self):
        currency1 = Mock()
        currency1.rate.rate = 1
        currency1.expense = 10
        currency1.income = 20
        currency1.balance = 10
        currency2 = Mock()
        currency2.rate.rate = 2
        currency2.expense = 10
        currency2.income = 20
        currency2.balance = 10
        target_currency = Mock()
        target_currency.rate.rate = 4
        target_currency.name = 'target_currency'
        qs = (currency1, currency2)
        result = get_report_total(qs, target_currency)
        expected = {'currency': 'target_currency', 'expense': 60.0, 'income': 120.0, 'balance': 60.0}
        self.assertEquals(result, expected)


    def test_get_transactions_currencies(self):
        AccountTransactionFactory.create_batch(2)
        qs = Transaction.objects.all()
        currencies = get_transactions_currencies(qs)
        self.assertEquals(len(currencies), 2)

    def test_get_multi_currency_category_stats(self):
        currency = CurrencyFactory(rate__rate=1)
        target_currency = CurrencyFactory(rate__rate=2)
        account1 = AccountFactory(user=self.user, currency=currency)
        account2 = AccountFactory(user=self.user, currency=target_currency)
        parent_category = CategoryFactory(user=self.user, type='E', parent=None)
        other_category = CategoryFactory(user=self.user, type='E', parent=None)
        child_category = CategoryFactory(user=self.user, type='E', parent=parent_category)
        transaction1 = AccountTransactionFactory(content_object=account1, amount=10, type='E', category=parent_category)
        transaction2 = AccountTransactionFactory(content_object=account2, amount=15, type='E', category=child_category)
        transaction3 = AccountTransactionFactory(content_object=account2, amount=25, type='E', category=child_category)
        transaction4 = AccountTransactionFactory(content_object=account2, amount=15, type='E', category=other_category)
        qs = Transaction.objects.all()
        stats = get_multi_currency_category_stats(qs, parent_category, self.user, target_currency=target_currency)
        self.assertEqual(stats[parent_category.name]['sum'], 20)
        self.assertEqual(stats[child_category.name]['sum'], 40)
    
    def test_get_multi_currency_main_category_stats(self):
        currency = CurrencyFactory(rate__rate=1)
        target_currency = CurrencyFactory(rate__rate=2)
        account1 = AccountFactory(user=self.user, currency=currency)
        account2 = AccountFactory(user=self.user, currency=target_currency)
        category = CategoryFactory(user=self.user, type='E', parent=None)
        transaction1 = AccountTransactionFactory(content_object=account1, amount=10, type='E', category=category)
        transaction2 = AccountTransactionFactory(content_object=account2, amount=15, type='E', category=category)
        qs = Transaction.objects.all()
        stats = get_multi_currency_main_category_stats(qs, 'E', self.user, target_currency=target_currency)
        self.assertEqual(stats[category.name]['sum'], 35)
        
    def test_get_multi_currency_category_json_stats(self):
        currency = CurrencyFactory(rate__rate=1)
        target_currency = CurrencyFactory(rate__rate=2)
        account1 = AccountFactory(user=self.user, currency=currency)
        account2 = AccountFactory(user=self.user, currency=target_currency)
        parent_category = CategoryFactory(user=self.user, type='E', parent=None)
        other_category = CategoryFactory(user=self.user, type='E', parent=None)
        child_category = CategoryFactory(user=self.user, type='E', parent=parent_category)
        transaction1 = AccountTransactionFactory(content_object=account1, amount=10, type='E', category=parent_category)
        transaction2 = AccountTransactionFactory(content_object=account2, amount=15, type='E', category=child_category)
        transaction3 = AccountTransactionFactory(content_object=account2, amount=25, type='E', category=child_category)
        transaction4 = AccountTransactionFactory(content_object=account2, amount=15, type='E', category=other_category)
        qs = Transaction.objects.all()
        stats = get_multi_currency_category_json_stats(qs, parent_category, self.user, target_currency=target_currency)
        self.assertEqual(stats['data'], [20,40])
        self.assertEqual(stats['labels'], [parent_category.name, child_category.name])

    def test_get_category_detail_stats(self):
        parent_category = CategoryFactory(parent=None, name='parent')
        category1 = CategoryFactory(parent=parent_category, name='cat1')
        category2 = CategoryFactory(parent=parent_category, name='cat2')
        category3 = CategoryFactory(parent=parent_category, name='cat3') #category with no transactions
        AccountTransactionFactory(name='qs', category=parent_category, amount=1)
        AccountTransactionFactory(name='qs', category=parent_category, amount=1)
        AccountTransactionFactory(category=parent_category, amount=1) #transaction not in the qs
        AccountTransactionFactory(name='qs', category=category1, amount=2)
        AccountTransactionFactory(name='qs', category=category1, amount=2)
        AccountTransactionFactory(category=category1, amount=2) #transaction not in the qs
        AccountTransactionFactory(name='qs', category=category2, amount=4)
        AccountTransactionFactory(name='qs', category=category2, amount=4)
        AccountTransactionFactory(category=category2, amount=4) #transaction not in the qs
        qs = Transaction.objects.filter(name='qs')
        result = get_category_detail_stats(qs, parent_category)
        expected = {
            'parent': {'sum': 2, 'id':parent_category.id},
            'cat1': {'sum': 4, 'id':category1.id},
            'cat2': {'sum': 8, 'id':category2.id},
        }
        self.assertEquals(result, expected)

    @patch('main.utils.convert_money')
    def test_convert_category_stats(self, mock):
        mock.return_value = 20
        stats = {'category': {'sum':10, 'id':1}}
        convert_category_stats(stats, 'from_currency', 'to_currency')
        self.assertEquals(stats['category']['sum'], 20)

    def test_add_category_stats(self):
        main_stats = {
            'category1': {'sum':10, id:1},
            'category3': {'sum':20, id:3},
        }
        added_stats = {
            'category1': {'sum':10, id:1},
            'category2': {'sum':30, id:2}
        }
        add_category_stats(main_stats, added_stats)
        expected_stats = {
            'category1': {'sum':20, id:1},
            'category2': {'sum':30, id:2},
            'category3': {'sum':20, id:3}
        }
        self.assertEquals(main_stats, expected_stats)

    def test_get_multi_currency_category_detail_stats(self):
        parent_category = CategoryFactory(parent=None, name='parent')
        category1 = CategoryFactory(parent=parent_category, name='cat1')
        category2 = CategoryFactory(parent=parent_category, name='cat2')
        currency1 = CurrencyFactory(rate__rate=1)
        currency2 = CurrencyFactory(rate__rate=2)
        account1 = AccountFactory(currency=currency1)
        account2 = AccountFactory(currency=currency2)
        AccountTransactionFactory(content_object=account1, category=parent_category, amount=1)
        AccountTransactionFactory(content_object=account2, category=parent_category, amount=5)
        AccountTransactionFactory(content_object=account1, category=category1, amount=2)
        AccountTransactionFactory(content_object=account2, category=category1, amount=5)
        AccountTransactionFactory(content_object=account1, category=category2, amount=3)
        AccountTransactionFactory(content_object=account2, category=category2, amount=5)
        qs = Transaction.objects.all()
        result = get_multi_currency_category_detail_stats(qs, parent_category, currency2)
        expected = {
            'parent': {'sum': 7, 'id':parent_category.id},
            'cat1': {'sum': 9, 'id':category1.id},
            'cat2': {'sum': 11, 'id':category2.id},
        }
        self.assertEquals(result, expected)

    @patch('main.utils.get_sorted_payment_plan')
    @patch('main.utils.add_installments_to_payment_plan')
    def test_get_credit_card_payment_plan(self, mock1, mock2):
        mock1.return_value = None
        mock2.return_value = {}
        card = Mock()
        card.transactions.filter.return_value = ["transaction1", "transaction2"]
        payment_plan = get_credit_card_payment_plan(card)
        self.assertIsInstance(payment_plan, dict)
        self.assertTrue(mock1.called)
        self.assertTrue(mock2.called)

    def test_get_transaction_installment_due_date(self):
        card = CreditCardFactory(payment_day=5)
        transaction_date = datetime.date(1999, 12, 13)
        installments = 5
        date = get_transaction_installment_due_date(transaction_date, installments, card)
        self.assertEquals(date, datetime.date(2000, 5, 5))

    @freeze_time("2003-03-03")
    def test_add_installments_to_payment_plan(self):
        card = CreditCardFactory(payment_day = 5) 
        expense = CreditCardTransactionFactory(installments=3, due_date=datetime.datetime(2003, 4, 5), amount=12)
        payment_plan = {}
        result = add_installments_to_payment_plan(expense, payment_plan, card)
        self.assertEquals(len(result), 2)

    def test_get_sorted_payment_plan(self):
        payment_plan = {datetime.date(2003, 3, 3): 5, datetime.date(2003, 3, 5): 15, datetime.date(2003, 2, 3): 25}
        sorted_paymet_plan = get_sorted_payment_plan(payment_plan)
        expected_plan = [[datetime.date(2003, 2, 3), 25], [datetime.date(2003, 3, 3), 5], [datetime.date(2003, 3, 5), 15]]
        self.assertEquals(sorted_paymet_plan, expected_plan)

    def test_convert_payment_plan_dates(self):
        payment_plan = [[datetime.date(2003, 2, 3), 25], [datetime.date(2003, 3, 3), 5], [datetime.date(2003, 3, 5), 15]]
        convert_payment_plan_dates(payment_plan)
        expected_plan = [['2003-02-03', 25], ['2003-03-03', 5], ['2003-03-05', 15]]
        self.assertEquals(payment_plan, expected_plan)

    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def test_create_guest_user(self):
        user = create_guest_user()
        self.assertTrue(User.objects.filter(username=user.username).exists())
        self.assertTrue(user.is_guest)

    def test_get_session_from_db(self):
        session_store = SessionStore()
        session_store.create()
        session_key = session_store.session_key
        request = Mock()
        request.session = session_store
        session_db = Session(session_key=session_key, expire_date=datetime.date(2003,1,1))
        session_db.save()
        result = get_session_from_db(request)
        self.assertEquals(result, session_db)

    def test_get_session_from_db_no_initial_session_on_db(self):
        session_store = SessionStore()
        session_store.create()
        session_key = session_store.session_key
        request = Mock()
        request.session = session_store
        result = get_session_from_db(request)
        self.assertEquals(result.session_key, session_key)

    def test_get_session_from_db_session_store_without_session_key(self):
        session_store = SessionStore(session_key=None)
        request = Mock()
        request.session = session_store
        result = get_session_from_db(request)
        self.assertEquals(Session.objects.first(), result)

    @patch('main.utils.create_guest_user')
    @patch('main.utils.get_session_from_db')
    @patch('main.utils.login')
    @patch('main.utils.create_guest_user_data')
    def test_setup_guest_user(self, data_mock, login_mock, session_mock, user_mock):
        user = UserFactoryNoSignal()
        session = SessionFactory()
        session_mock.return_value = session
        request = Mock()
        user_mock.return_value = user
        result = setup_guest_user(request)
        self.assertEquals(user, result)
        self.assertTrue(GuestUserSession.objects.all().exists())
        self.assertEquals(GuestUserSession.objects.first().session, session)
        self.assertTrue(login_mock.called_once)
        self.assertTrue(data_mock.called_once)

    @patch("main.utils.create_guest_user_accounts")
    def test_create_guest_user_data(self, accounts_mock):
        user = Mock()
        create_guest_user_data(user)
        self.assertTrue(accounts_mock.called_once)

    @freeze_time("2000-05-01")
    def test_create_guest_user_accounts(self):
        user = UserFactoryNoSignal()
        user_preferences = UserPreferencesFactory(user=user)
        user_accounts = create_guest_user_accounts(user)
        for key, value in user_accounts.items():
            self.assertEquals(value.user, user)
            self.assertEquals(value.created.date().__str__(), "2000-01-22")
