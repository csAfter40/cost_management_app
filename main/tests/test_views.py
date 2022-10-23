from decimal import Decimal
import json
import factory
import unittest
from wallet.settings import TESTING_ATOMIC
from .factories import CategoryFactory, AccountTransactionFactory, TransactionFactory, TransferFactory, UserFactoryNoSignal, UserPreferencesFactory
from .cbv_test_mixins import (
    TestCreateViewMixin,
    TestListViewMixin,
    TestUpdateViewMixin,
    TestDetailViewMixin,
    TestDeleteViewMixin
)
from main.forms import TransferForm, ExpenseInputForm, IncomeInputForm
from main.models import Account, Category, Loan, Transaction, Transfer, User, UserPreferences
from main.tests.mixins import BaseViewTestMixin, UserFailTestMixin
from .factories import AccountFactory, CurrencyFactory, LoanFactory
from django.urls import reverse, resolve
from django.db import models
from django.db.models import signals
from django.test import TestCase, TransactionTestCase
from django.http import HttpRequest, JsonResponse
from main import views
from django.db import models
from datetime import date


class TestIndex(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:index')
        cls.template = 'main/index.html'  # str 'app_name/template_name.html'
        cls.view_function = views.index  # Add .as_view()
        cls.user_factory = UserFactoryNoSignal

    def test_page_redirects_if_user_is_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(self.test_url)
        self.assertRedirects(response, reverse('main:main'), 302, 200)


class TestCreateAccountView(TestCreateViewMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:create_account')
        cls.success_url = reverse('main:main')
        cls.model = Account
        cls.context_list = ('form', )
        cls.template = 'main/create_account.html'
        cls.view_function = views.CreateAccountView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

    def setUp(self) -> None:
        super().setUp()
        currency = CurrencyFactory()
        self.valid_data = [
            {
                'name': 'sample_account',
                'balance': Decimal(12.00),
                'currency': currency.id,
            },
            {
                'name': 'sample_account2',
                'balance': Decimal(-32.00),
                'currency': currency.id,
            },
        ]
        self.invalid_data = [
            {
                'name': 'sample_account',
                'balance': 'abc', # balance must be a number.
                'currency': currency.id,
            },
        ]        

    def subtest_post_success(self, data):
        super().subtest_post_success(data)
        self.assertEquals(self.user, self.valid_object.user)
    

class TestCreateLoanView(TestCreateViewMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:create_loan')
        cls.success_url = reverse('main:main')
        cls.model = Loan
        cls.context_list = ('form', )
        cls.template = 'main/create_loan.html'
        cls.view_function = views.CreateLoanView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

    def setUp(self) -> None:
        super().setUp()
        currency = CurrencyFactory()
        self.valid_data = [
            {
                'name': 'sample_loan',
                'balance': Decimal(12.00),
                'currency': currency.id,
            },
            {
                'name': 'sample_loan2',
                'balance': Decimal(-32.00),
                'currency': currency.id,
            },
        ]
        self.invalid_data = [
            {
                'name': 'sample_loan',
                'balance': 'abc', # balance must be a number.
                'currency': currency.id,
            },
        ]    
    

    def subtest_post_success(self, data):
        response = self.client.post(self.test_url, data=data)
        # test response code
        self.assertRedirects(response, 
            self.success_url, 
            status_code=302, 
            target_status_code=200, 
            fetch_redirect_response=True
        )
        # test created object
        self.valid_object = self.get_object()
        self.assertNotEqual(self.valid_object, None)
        for key, value in data.items():
            if isinstance(getattr(self.valid_object, key), models.Model):
                self.assertEquals(getattr(self.valid_object, key).id, value)
            elif isinstance(getattr(self.valid_object, key), Decimal):
                self.assertEquals(getattr(self.valid_object, key), -abs(value))
            else:
                self.assertEquals(getattr(self.valid_object, key), value)


class TestDuplicateAccountCreateData(TransactionTestCase):
    
    def setUp(self) -> None:
        self.user = UserFactoryNoSignal()
        self.client.force_login(self.user)
        duplicate_account = AccountFactory(user=self.user, name='duplicate')
        self.test_url = '/accounts/create'
        currency = CurrencyFactory()
        self.data={
            'name': 'duplicate',
            'balance': Decimal(20.00),
            'currency': currency.id,
        }

    def test_duplicate_account(self):
        pre_test_object_qty = Account.objects.count()
        response = self.client.post(self.test_url, self.data)
        self.assertEquals(response.status_code, 200)
        post_test_object_qty = Account.objects.count()
        self.assertEquals(pre_test_object_qty, post_test_object_qty)


class TestDuplicateLoanCreateData(TransactionTestCase):
    
    def setUp(self) -> None:
        self.user = UserFactoryNoSignal()
        self.client.force_login(self.user)
        duplicate_account = LoanFactory(user=self.user, name='duplicate')
        self.test_url = '/loans/create'
        currency = CurrencyFactory()
        self.data={
            'name': 'duplicate',
            'balance': Decimal(20.00),
            'currency': currency.id,
        }

    def test_duplicate_account(self):
        pre_test_object_qty = Loan.objects.count()
        response = self.client.post(self.test_url, self.data)
        self.assertEquals(response.status_code, 200)
        post_test_object_qty = Loan.objects.count()
        self.assertEquals(pre_test_object_qty, post_test_object_qty)


class TestAccountsView(TestListViewMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:accounts')
        cls.model = Account
        cls.context_list = ['object_list']
        cls.template = 'main/accounts.html'
        cls.view_function = views.AccountsView.as_view()
        cls.login_required = True
        cls.model_factory = AccountFactory
        cls.user_factory = UserFactoryNoSignal

    def test_queryset(self):
        if self.model_factory:
            # active accounts belongs to self.user
            self.model_factory.create_batch(5, user=self.user)
            # deleted accounts belongs to self.user
            self.model_factory.create_batch(5, user=self.user, is_active=False)
            # active accounts doesn't belong to self.user
            self.model_factory.create_batch(5)
            # deleted accounts doesn't belong to self.user
            self.model_factory.create_batch(5, is_active=False)
            qs = self.model.objects.filter(user=self.user, is_active=True)
            response = self.client.get(self.test_url)
            context_qs = response.context[self.object_list_name]
            self.assertQuerysetEqual(qs, context_qs, ordered=False)


class TestEditAccountView(TestUpdateViewMixin, UserFailTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url_pattern = '/accounts/<pk>/edit'
        cls.success_url = reverse('main:main')
        cls.model = Account
        cls.context_list = ('form', )
        cls.template = 'main/account_update.html'
        cls.view_function = views.EditAccountView.as_view()
        cls.login_required = True
        cls.model_factory = AccountFactory
        cls.user_factory = UserFactoryNoSignal

    def setUp(self) -> None:
        super().setUp()
        currency = CurrencyFactory()
        duplicate_account = AccountFactory(user=self.user, name='duplicate')
        self.valid_data = [
            {
                'name': 'new_account_name',
                'balance': Decimal(20.00),
                'currency': currency.id,
            },
        ]
        self.invalid_data = [
            {
                'name': 'new_account_name',
                'balance': Decimal(20.00),
                'currency': 'XYZ',
            },
            {
                'name': 'new_account_name',
                'balance': 'abc',
                'currency': currency.id,
            },
        ]    

    def set_object(self):
        super().set_object()
        self.object.user = self.user
        self.object.save()
    

class TestDuplicateAccountUpdateData(TransactionTestCase):

    def setUp(self) -> None:
        self.user = UserFactoryNoSignal()
        self.client.force_login(self.user)
        self.object = AccountFactory(user=self.user)
        duplicate_account = AccountFactory(user=self.user, name='duplicate')
        self.test_url = f'/accounts/{self.object.id}/edit'
        currency = CurrencyFactory()
        self.data={
            'name': 'duplicate',
            'balance': Decimal(20.00),
            'currency': currency.id,
        }

    def test_duplicate_account(self):
        pre_update_values = self.object.__dict__
        response = self.client.post(self.test_url, self.data)
        self.assertEquals(response.status_code, 200)
        self.object.refresh_from_db()
        post_update_values = self.object.__dict__
        self.assertEquals(pre_update_values, post_update_values)


class TestDuplicateLoanUpdateData(TransactionTestCase):

    def setUp(self) -> None:
        self.user = UserFactoryNoSignal()
        self.client.force_login(self.user)
        self.object = LoanFactory(user=self.user)
        duplicate_account = LoanFactory(user=self.user, name='duplicate')
        self.test_url = f'/loans/{self.object.id}/edit'
        currency = CurrencyFactory()
        self.data={
            'name': 'duplicate',
            'balance': Decimal(20.00),
            'currency': currency.id,
        }

    def test_duplicate_account(self):
        pre_update_values = self.object.__dict__
        response = self.client.post(self.test_url, self.data)
        self.assertEquals(response.status_code, 200)
        self.object.refresh_from_db()
        post_update_values = self.object.__dict__
        self.assertEquals(pre_update_values, post_update_values)
    

class TestMainView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:main')
        cls.context_list = [
            "accounts",
            "loans",
            "expense_form",
            "income_form",
            "transfer_form",
            "transactions",
            "transfers",
            "account_data",
            "show_account",
        ]
        cls.template = 'main/main.html'
        cls.view_function = views.main
        cls.user_factory = UserFactoryNoSignal
        cls.login_required = True

    def test_loans_list(self):
        LoanFactory.create_batch(5)
        LoanFactory.create_batch(5, user=self.user)
        LoanFactory.create_batch(5, user=self.user, is_active=False)
        qs = Loan.objects.filter(user=self.user, is_active=True)
        response = self.client.get(self.test_url)
        context_qs = response.context['loans']
        self.assertQuerysetEqual(qs, context_qs, ordered=False)
    
    def test_accounts_list(self):
        AccountFactory.create_batch(5)
        AccountFactory.create_batch(5, user=self.user)
        AccountFactory.create_batch(5, user=self.user, is_active=False)
        qs = Account.objects.filter(user=self.user, is_active=True)
        response = self.client.get(self.test_url)
        context_qs = response.context['accounts']
        self.assertQuerysetEqual(qs, context_qs, ordered=False)

    def test_latest_transactions_list(self):
        AccountTransactionFactory.create_batch(
            10, 
            content_object__user=self.user, 
            category__is_transfer=False
        )
        AccountTransactionFactory.create_batch(
            10, 
            content_object__user=self.user, 
            category__is_transfer=True
        )
        AccountTransactionFactory.create_batch(10)
        accounts_list = Account.objects.filter(user=self.user).values_list('id', flat=True)
        transactions = (
            Transaction.objects.filter(content_type__model='account', object_id__in=accounts_list)
            .exclude(category__is_transfer=True)
            .order_by('-date')[:5]
        ) 
        response = self.client.get(self.test_url)
        context_qs = response.context['transactions']
        self.assertQuerysetEqual(transactions, context_qs, ordered=True)
        
    def test_latest_transfers_list(self):
        TransferFactory.create_batch(10)
        TransferFactory.create_batch(10, user=self.user)
        qs = Transfer.objects.filter(user=self.user).order_by('-date')[:5]
        response = self.client.get(self.test_url)
        self.assertQuerysetEqual(
            qs, 
            response.context['transfers'], 
            ordered=True
        )
        
    def test_form_instances(self):
        response = self.client.get(self.test_url)
        self.assertIsInstance(response.context['expense_form'], ExpenseInputForm)
        self.assertIsInstance(response.context['transfer_form'], TransferForm)
        self.assertIsInstance(response.context['income_form'], IncomeInputForm)

    def test_account_data(self):
        AccountFactory.create_batch(5, user=self.user)
        response = self.client.get(self.test_url)
        account_data = response.context['account_data']
        for key, value in account_data.items():
            self.assertIsInstance(value, str)
            self.assertTrue(len(value)<=3)

    def test_show_account(self):
        response = self.client.get(self.test_url)
        self.assertIsInstance(response.context['show_account'], bool)

    def test_post_transfer_success(self):
        CategoryFactory(user=self.user, name='Transfer Out', parent=None)
        CategoryFactory(user=self.user, name='Transfer In', parent=None)
        from_account = AccountFactory(user=self.user)
        to_account = AccountFactory(user=self.user)
        data = {
            'submit-transfer': True,
            'from_account': from_account.id,
            'from_amount': 12,
            'to_account': to_account.id,
            'to_amount': 14,
            'date': date.today()
        }
        response = self.client.post(self.test_url, data)
        self.assertRedirects(
            response, 
            reverse('main:main'), 
            status_code=302, 
            target_status_code=200, 
            fetch_redirect_response=True
        )
        self.assertTrue(
            Transfer.objects.all().exists(), 
            msg='Transfer object not created.'
        )
        transfer_obj = Transfer.objects.last()
        self.assertEquals(
            data['from_account'], 
            transfer_obj.from_transaction.object_id,
            msg="From account value not matching",
        )
        self.assertEquals(
            data['from_amount'], 
            transfer_obj.from_transaction.amount,
            msg="From amount value not matching",
        )
        self.assertEquals(
            data['to_account'], 
            transfer_obj.to_transaction.object_id,
            msg="To account value not matching",
        )
        self.assertEquals(
            data['to_amount'], 
            transfer_obj.to_transaction.amount,
            msg="To amount value not matching",
        )
        self.assertEquals(
            data['date'], 
            transfer_obj.date,
            msg="Date value not matching",
        )
        self.assertEquals(
            self.user, 
            transfer_obj.user,
            msg="Object.user not matching with test user",
        )
    
    def test_post_transfer_failure(self):
        data = {
            'submit-transfer': True,
            'from_account': 'invalid_data',
            'from_amount': 'invalid_data',
            'to_account': 'invalid_data',
            'to_amount': 14,
            'date': date.today()
        }
        response = self.client.post(self.test_url, data)
        self.assertEquals(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertEquals(content.count('invalid-feedback'), 3, msg='Error count not matching')

    def test_post_expense_success(self):
        category = CategoryFactory(
            user=self.user, 
            parent=None, 
            type='E', 
            is_transfer=False
        )
        account = AccountFactory(user=self.user)
        data = {
            'submit-expense': True,
            'name': 'test_transfer',
            'content_object': account.id,
            'amount': 12,
            'category': category.id,
            'date': date.today(),
            'type': 'E'
        }
        response = self.client.post(self.test_url, data)
        self.assertRedirects(
            response, 
            reverse('main:main'), 
            status_code=302, 
            target_status_code=200, 
            fetch_redirect_response=True
        )
        self.assertTrue(
            Transaction.objects.all().exists(), 
            msg='Transfer object not created.'
        )
        transaction_obj = Transaction.objects.last()
        self.assertEquals(
            data['name'], 
            transaction_obj.name,
            msg="Name value not matching",
        )
        self.assertEquals(
            data['content_object'], 
            transaction_obj.object_id,
            msg="Account id value not matching",
        )
        self.assertEquals(
            data['amount'], 
            transaction_obj.amount,
            msg="Amount value not matching",
        )
        self.assertEquals(
            data['category'], 
            transaction_obj.category.id,
            msg="Category id value not matching",
        )
        self.assertEquals(
            data['date'], 
            transaction_obj.date,
            msg="Date value not matching",
        )
        self.assertEquals(
            data['type'], 
            transaction_obj.type,
            msg="Type value not matching",
        )

    def test_post_expense_failure(self):
        data = {
            'submit-expense': True,
            'name': 'test_transfer',
            'account': 'invalid_data',
            'amount': 'invalid_data',
            'category': 'invalid_data',
            'date': date.today(),
            'type': 'E'
        }
        response = self.client.post(self.test_url, data)
        self.assertEquals(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertEquals(content.count('invalid-feedback'), 3, msg='Error count not matching')

    def test_post_income_success(self):
        category = CategoryFactory(
            user=self.user, 
            parent=None, 
            type='I', 
            is_transfer=False
        )
        account = AccountFactory(user=self.user)
        data = {
            'submit-income': True,
            'name': 'test_transfer',
            'content_object': account.id,
            'amount': 12,
            'category': category.id,
            'date': date.today(),
            'type': 'I'
        }
        response = self.client.post(self.test_url, data)
        self.assertRedirects(
            response, 
            reverse('main:main'), 
            status_code=302, 
            target_status_code=200, 
            fetch_redirect_response=True
        )
        self.assertTrue(
            Transaction.objects.all().exists(), 
            msg='Transfer object not created.'
        )
        transaction_obj = Transaction.objects.last()
        self.assertEquals(
            data['name'], 
            transaction_obj.name,
            msg="Name value not matching",
        )
        self.assertEquals(
            data['content_object'], 
            transaction_obj.object_id,
            msg="Account id value not matching",
        )
        self.assertEquals(
            data['amount'], 
            transaction_obj.amount,
            msg="Amount value not matching",
        )
        self.assertEquals(
            data['category'], 
            transaction_obj.category.id,
            msg="Category id value not matching",
        )
        self.assertEquals(
            data['date'], 
            transaction_obj.date,
            msg="Date value not matching",
        )
        self.assertEquals(
            data['type'], 
            transaction_obj.type,
            msg="Type value not matching",
        )
    
    def test_post_income_failure(self):
        data = {
            'submit-income': True,
            'name': 'test_transfer',
            'account': 'invalid_data',
            'amount': 'invalid_data',
            'category': 'invalid_data',
            'date': date.today(),
            'type': 'I'
        }
        response = self.client.post(self.test_url, data)
        self.assertEquals(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertEquals(content.count('invalid-feedback'), 3, msg='Error count not matching')


class TestTransactionNameAutocomplete(BaseViewTestMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:transaction_name_autocomplete')
        cls.view_function = views.transaction_name_autocomplete
        cls.user_factory = UserFactoryNoSignal
        cls.login_required = True

    def test_get(self):
        for i in range(6):
            AccountTransactionFactory(name=f'match_E{i}', type='E', content_object__user=self.user)
        for i in range(5):
            AccountTransactionFactory(name=f'fail{i}', type='E', content_object__user=self.user)
        for i in range(7):
            AccountTransactionFactory(name=f'match_I{i}', type='I', content_object__user=self.user)
        for Accounti in range(5):
            AccountTransactionFactory(name=f'fail{i}', type='I', content_object__user=self.user)
        for Accounti in range(5):
            AccountTransactionFactory(name=f'match{i}', type='E')
        for Accounti in range(5):
            AccountTransactionFactory(name=f'fail{i}', type='E')
        for Accounti in range(5):
            AccountTransactionFactory(name=f'match{i}', type='I')
        for Accounti in range(5):
            AccountTransactionFactory(name=f'fail{i}', type='I')
        data_set = [
            {'name': 'mat', 'type': 'I', 'count':7},
            {'name': 'mat', 'type': 'E', 'count':6},
            {'name': 'none', 'type': 'I', 'count':0}
        ]
        for data in data_set:
            with self.subTest(data=data):
                response = self.client.get(self.test_url, data)
                self.assertEquals(response.status_code, 200)
                self.assertIsInstance(response, JsonResponse)
                content = json.loads(response.content)
                self.assertEquals(len(content['data']), data['count'])
                for match in content['data']:
                    self.assertIn(data['name'], match)


class TestLoginView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:login')
        cls.template = 'main/login.html'
        cls.view_function = views.LoginView.as_view()
        cls.success_url = reverse('main:main')
        cls.next_url = reverse('main:accounts')
        cls.user_factory = UserFactoryNoSignal
        cls.context_list = []
        
    def setUp(self) -> None:
        self.password = 'testpassword'
        self.user = self.get_user()

    def get_user(self):
        user = UserFactoryNoSignal(username='testuser')
        user.set_password(self.password)
        user.save()
        return user

    def test_post(self):
        from django.contrib.auth import get_user
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
        data = {
            'username': self.user.username, 
            'password': self.password,
            'next': ''
        }
        response = self.client.post(self.test_url, data)
        self.assertRedirects(response, 
            self.success_url, 
            status_code=302, 
            target_status_code=200, 
            fetch_redirect_response=True
        )
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_post_with_next(self):
        data = {
            'username': self.user.username, 
            'password': self.password,
            'next': self.next_url,
        }
        response = self.client.post(self.test_url, data)
        self.assertRedirects(response, 
            self.next_url, 
            status_code=302, 
            target_status_code=200, 
            fetch_redirect_response=True
        )
    
    def test_post_invalid_data(self):
        data = {
            'username': self.user.username, 
            'password': 'invalid_password',
            'next': '',
        }
        response = self.client.post(self.test_url, data)
        self.assertRedirects(response, 
            self.test_url, 
            status_code=302, 
            target_status_code=200, 
            fetch_redirect_response=True
        )
        self.assertIsNotNone(response.cookies.get('messages', None))

    def test_redirect_if_user_is_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(self.test_url)
        self.assertRedirects(response, reverse('main:main'), 302, 200)


class TestRegisterView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:register')
        cls.template = 'main/register.html'
        cls.view_function = views.RegisterView.as_view()
        cls.success_url = reverse('main:setup')
        cls.error_url = reverse('main:register')
        cls.user_factory = UserFactoryNoSignal
        cls.context_list = []

    def get_user(self):
        user = UserFactoryNoSignal(username='testuser')
        return user

    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def test_post(self):
        data = {
            'username': 'new_user', 
            'email': 'new_user@example.com',
            'password': 'password',
            'confirmation': 'password',
        }
        response = self.client.post(self.test_url, data)
        self.assertRedirects(response, 
            self.success_url, 
            status_code=302, 
            target_status_code=200, 
            fetch_redirect_response=True
        )

    def test_post_password_not_matching(self):
        data = {
            'username': 'new_user', 
            'email': 'new_user@example.com',
            'password': 'password',
            'confirmation': 'not_matching',
        }
        response = self.client.post(self.test_url, data)
        self.assertRedirects(response, 
            self.error_url, 
            status_code=302, 
            target_status_code=200, 
            fetch_redirect_response=True
        )
        self.assertIsNotNone(response.cookies.get('messages', None))

    def test_post_password_duplicate_user(self):
        data = {
            'username': self.user.username, 
            'email': self.user.email,
            'password': 'password',
            'confirmation': 'password',
        }
        response = self.client.post(self.test_url, data)
        self.assertRedirects(response, 
            self.error_url, 
            status_code=302, 
            target_status_code=200, 
            fetch_redirect_response=True
        )
        self.assertIsNotNone(response.cookies.get('messages', None))
    

class TestSetupView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:setup')
        cls.redirect_url = reverse('main:main')
        cls.context_list = ['form']
        cls.template = 'main/setup.html'
        cls.post_method = True
        cls.get_method = True
        cls.view_function = views.SetupView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

    def setUp(self) -> None:
        super().setUp()
        user_preferences = UserPreferencesFactory(user=self.user)
        currency = CurrencyFactory()
        self.post_data = {'currency': currency.id}

        
class TestCheckUsername(BaseViewTestMixin, TestCase):
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:check_username')
        cls.view_function = views.check_username
        cls.user_factory = UserFactoryNoSignal

    def get_user(self):
        user = UserFactoryNoSignal(username='testuser')
        return user

    def test_get(self):
        response = self.client.post(self.test_url, {'username': 'testuser'})
        self.assertEquals(response.status_code, 200)
        self.assertIn('This username exists', response.content.decode('utf-8'))
        response = self.client.post(self.test_url, {'username': 'new_username'})
        self.assertEquals(response.status_code, 200)
        self.assertIn('This username is available', response.content.decode('utf-8'))
        response = self.client.post(self.test_url, {'username': 'aa'}) # username length < 3 
        self.assertEquals(response.status_code, 200)
        self.assertNotIn('This username', response.content.decode('utf-8'))


class TestLogoutView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.get_method = False
        cls.test_url = reverse('main:logout')
        cls.redirect_url = reverse('main:index')
        cls.post_method = True
        cls.view_function = views.logout_view
        cls.user_factory = UserFactoryNoSignal
        cls.context_list = []

    def test_post(self): 
        from django.contrib.auth import get_user   
        super().test_post()
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)


class TestAccountDetailAjaxView(UserFailTestMixin, BaseViewTestMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = ''
        cls.context_list = [
            "transactions",
            "stats",
            "account",
            "expense_stats",
            "income_stats",
            "comparison_stats",
        ]
        cls.template = 'main/account_detail_pack.html'
        cls.view_function = views.AccountDetailAjaxView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal
        cls.model = Account

    def setUp(self) -> None:
        super().setUp()
        self.object = AccountFactory(user=self.user)
        self.test_url = reverse('main:account_detail_ajax', kwargs={'pk':self.object.id})

    def subtest_get(self, test_url):
        response = self.client.get(test_url)
        self.assertEquals(response.status_code, 200)
        # test template
        self.assertTemplateUsed(response, self.template)
        # test context
        for item in self.context_list:
                self.assertIn(item, response.context.keys())
        
    def test_get(self):    
        times = ('all', 'week', 'month', 'year')
        object = AccountFactory(user=self.user)
        for time in times:
            with self.subTest(time):
                test_url = self.test_url + f'?time={time}'
                self.subtest_get(test_url)

    def test_account_not_active(self):
        self.object.is_active = False
        self.object.save()
        response = self.client.get(self.test_url)
        self.assertEquals(response.status_code, 404)
     

class TestAccountDetailSubcategoryAjaxView(UserFailTestMixin, BaseViewTestMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = ''
        cls.view_function = views.AccountDetailSubcategoryAjaxView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal
        cls.model = Account

    def setUp(self) -> None:
        super().setUp()
        self.object = AccountFactory(user=self.user)
        self.category = CategoryFactory(parent=None, user=self.user)
        self.test_url = reverse(
                            'main:account_detail_subcategory_ajax', 
                            kwargs = {
                                        'pk':self.object.id, 
                                        'cat_pk':self.category.id
                                     }
                        )

    def subtest_get(self, test_url):
        response = self.client.get(test_url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['content-type'], 'application/json')
        
    def test_get(self):    
        AccountTransactionFactory.create_batch(
            20, 
            category=self.category, 
            content_object=self.object
        )
        times = ('all', 'week', 'month', 'year')
        for time in times:
            with self.subTest(time):
                test_url = self.test_url + f'?time={time}'
                self.subtest_get(test_url)

    def test_account_not_active(self):
        self.object.is_active = False
        self.object.save()
        response = self.client.get(self.test_url)
        self.assertEquals(response.status_code, 404)


class TestAccountDetailView(UserFailTestMixin, BaseViewTestMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = ''
        cls.context_list = [
            'account',
            'transactions',
            'stats',
            'expense_stats',
            'income_stats',
            'comparison_stats'
        ]
        cls.template = 'main/account_detail.html'
        cls.view_function = views.AccountDetailView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

    def setUp(self) -> None:
        super().setUp()
        self.object = AccountFactory(user=self.user)
        self.test_url = reverse(
            'main:account_detail', 
            kwargs={'pk':self.object.id}
        )

    def test_get(self):    
        AccountTransactionFactory.create_batch(20, content_object=self.object)
        super().test_get()
    
    def test_get_account_not_active(self):
        self.object.is_active = False
        self.object.save()
        response = self.client.get(self.test_url)
        self.assertEquals(response.status_code, 404)


class TestDeleteAccountView(UserFailTestMixin, BaseViewTestMixin, TestCase):
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.redirect_url = reverse('main:main')
        cls.post_method = True
        cls.get_method = False
        cls.view_function = views.DeleteAccountView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal
        cls.test_url = ''
    
    def setUp(self) -> None:
        super().setUp()
        CategoryFactory(user=self.user, type='E', name='Asset Delete', parent=None)
        CategoryFactory(user=self.user, type='I', name='Asset Delete', parent=None)
        self.object = AccountFactory(user=self.user, balance=0)
        self.test_url = reverse('main:delete_account', kwargs={'pk':self.object.id})

    def test_inactive_account(self):
        inactive_account = AccountFactory(user=self.user, is_active=False)
        test_url = reverse('main:delete_account', kwargs={'pk':inactive_account.id})
        response = self.client.post(test_url, {})
        self.assertEquals(response.status_code, 404)

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.post(self.test_url, self.post_data)
        self.assertEquals(response.status_code, 302)

    def test_with_positive_balance_account(self):
        account = AccountFactory(user=self.user, balance=100)
        test_url = reverse('main:delete_account', kwargs={'pk':account.id})
        self.client.post(test_url)
        transaction = Transaction.objects.first()
        self.assertEquals(transaction.amount, 100)
        self.assertEquals(transaction.type, 'E')

    def test_with_negative_balance_account(self):
        account = AccountFactory(user=self.user, balance=-100)
        test_url = reverse('main:delete_account', kwargs={'pk':account.id})
        self.client.post(test_url)
        transaction = Transaction.objects.first()
        self.assertEquals(transaction.amount, 100)
        self.assertEquals(transaction.type, 'I')

class TestDeleteLoanView(UserFailTestMixin, BaseViewTestMixin, TestCase):
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = ''
        cls.redirect_url = reverse('main:main')
        cls.post_method = True
        cls.get_method = False
        cls.view_function = views.DeleteLoanView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal
    
    def setUp(self) -> None:
        super().setUp()
        CategoryFactory(user=self.user, type='E', name='Asset Delete', parent=None)
        CategoryFactory(user=self.user, type='I', name='Asset Delete', parent=None)
        self.object = LoanFactory(user=self.user)
        self.test_url = reverse('main:delete_loan', kwargs={'pk':self.object.id})

    def test_inactive_loan(self):
        inactive_loan = LoanFactory(is_active=False)
        test_url = reverse('main:delete_account', kwargs={'pk':inactive_loan.id})
        response = self.client.post(test_url, {})
        self.assertEquals(response.status_code, 404)

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.post(self.test_url, self.post_data)
        self.assertEquals(response.status_code, 302)

    def test_with_positive_balance_loan(self):
        account = AccountFactory(user=self.user, balance=100)
        test_url = reverse('main:delete_account', kwargs={'pk':account.id})
        self.client.post(test_url)
        transaction = Transaction.objects.first()
        self.assertEquals(transaction.amount, 100)
        self.assertEquals(transaction.type, 'E')

    def test_with_negative_balance_loan(self):
        account = AccountFactory(user=self.user, balance=-100)
        test_url = reverse('main:delete_account', kwargs={'pk':account.id})
        self.client.post(test_url)
        transaction = Transaction.objects.first()
        self.assertEquals(transaction.amount, 100)
        self.assertEquals(transaction.type, 'I')

class TestLoanDetailView(UserFailTestMixin, TestDetailViewMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url_pattern = '/loans/<pk>'
        cls.context_list = ['progress', 'transactions', 'payment_stats', 'form']
        cls.template = 'main/loan_detail.html'
        cls.get_method = True
        cls.view_function = views.LoanDetailView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal
        cls.model = Loan
        cls.model_factory = LoanFactory
        cls.object_context_name = 'object'

    def setUp(self):
        super().setUp()
        self.object.user = self.user
        self.object.save()  


class TestLoanDetailAjaxView(UserFailTestMixin, BaseViewTestMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = ''
        cls.context_list = [
            "transactions",
        ]
        cls.template = 'main/loan_detail_pack.html'
        cls.view_function = views.LoanDetailAjaxView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal
        cls.model = Loan

    def setUp(self) -> None:
        super().setUp()
        self.object = LoanFactory(user=self.user)
        self.test_url = reverse('main:loan_detail_ajax', kwargs={'pk':self.object.id})
        
    def test_get(self):    
        response = self.client.get(self.test_url)
        self.assertEquals(response.status_code, 200)
        # test template
        self.assertTemplateUsed(response, self.template)
        # test context
        for item in self.context_list:
                self.assertIn(item, response.context.keys())
        
    def test_laon_not_active(self):
        self.object.is_active = False
        self.object.save()
        response = self.client.get(self.test_url)
        self.assertEquals(response.status_code, 404)
     

class TestEditLoanView(TestUpdateViewMixin, UserFailTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url_pattern = '/loans/<pk>/edit'
        cls.success_url = reverse('main:main')
        cls.model = Loan
        cls.context_list = ('form', )
        cls.template = 'main/loan_update.html'
        cls.view_function = views.EditLoanView.as_view()
        cls.login_required = True
        cls.model_factory = LoanFactory
        cls.user_factory = UserFactoryNoSignal

    def setUp(self) -> None:
        super().setUp()
        currency = CurrencyFactory()
        self.valid_data = [
            {
                'name': 'new_loan_name',
                'balance': Decimal(20.00),
                'currency': currency.id,
            },
        ]
        self.invalid_data = [
            {
                'name': 'new_loan_name',
                'balance': Decimal(20.00),
                'currency': 'XYZ',
            },
            {
                'name': 'new_loan_name',
                'balance': 'abc',
                'currency': currency.id,
            },
        ]    

    def set_object(self):
        super().set_object()
        self.object.user = self.user
        self.object.save()

    def subtest_post_success(self, data):
        response = self.client.post(self.test_url, data=data)
        self.assertRedirects(response, self.success_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        # get updated object values from db
        self.object.refresh_from_db()
        for key, value in data.items():
            if isinstance(getattr(self.object, key), models.Model):
                self.assertEquals(getattr(self.object, key).id, value)
            elif key == 'balance':
                self.assertEquals(getattr(self.object, key), -abs(value))
            else:
                self.assertEquals(getattr(self.object, key), value)


class TestPayLoanView(BaseViewTestMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:pay_loan')
        cls.redirect_url = reverse('main:main')
        cls.context_list = ['account_data', 'loan_data', 'form']
        cls.template = 'main/loan_pay.html'
        cls.post_method = False
        cls.get_method = True
        cls.view_function = views.PayLoanView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

    def setUp(self):
        super().setUp()
        CategoryFactory(user=self.user, name='Pay Loan', parent=None)
        currency = CurrencyFactory()
        account = AccountFactory(user=self.user, currency=currency)
        loan = LoanFactory(user=self.user, currency=currency)
        self.valid_data = [
            {
                'amount': 1000,
                'date': date.today(),
                'account': account.id,
                'loan': loan.id,
            }
        ]
        self.invalid_data = [
            {
                'amount': 'abc',
                'date': date.today(),
                'account': account.id,
                'loan': loan.id,
            },
            {
                'amount': 1000,
                'date': date.today(),
                'account': 'abc',
                'loan': loan.id,
            },
        ]

    def subtest_valid_post(self, data):
        response = self.client.post(self.test_url, data)
        self.assertRedirects(
            response, 
            self.redirect_url, 
            302, 
            200, 
            fetch_redirect_response=True
        )
        self.assertEquals(Transfer.objects.count(), 1)
        self.assertEquals(Transaction.objects.count(), 2)

    def test_post_valid(self):
        for data in self.valid_data:
            with self.subTest(data):
                self.subtest_valid_post(data)

    def subtest_invalid_post(self, data):
        response = self.client.post(self.test_url, data)
        self.assertEquals(response.status_code, 200)

    def test_post_invalid(self):
        for data in self.invalid_data:
            with self.subTest(data):
                self.subtest_invalid_post(data)
    
    @unittest.skip('will be implemented')
    def test_atomic_transaction(self):
        data = self.valid_data[0]
        before_transaction_qty = Transaction.objects.all().count()
        with self.settings(TESTING_ATOMIC=True):
            response = self.client.post(self.test_url, data)
            after_transaction_qty = Transaction.objects.all().count()
            self.assertEquals(response.status_code, 200)
            self.assertEquals(before_transaction_qty, after_transaction_qty)


class TestCategoriesView(BaseViewTestMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:categories')
        cls.context_list = ['expense_categories', 'income_categories']
        cls.template = 'main/categories.html'
        cls.view_function = views.CategoriesView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal


class TestCreateExpenseCategory(UserFailTestMixin, BaseViewTestMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:create_expense_category')
        cls.redirect_url = reverse('main:categories')
        cls.get_method = False
        cls.view_function = views.CreateExpenseCategory.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

    def setUp(self) -> None:
        super().setUp()
        self.parent_category = CategoryFactory(user=self.user, parent=None)
        duplicate_category = CategoryFactory(
            user=self.user, 
            parent=self.parent_category, 
            name='duplicate_category',
            type='E'
        )
        duplicate_category_parent_none = CategoryFactory(
            user=self.user, 
            parent=None, 
            name='duplicate_category',
            type='E'
        )
        self.post_valid_data = [
            {
                'category_id':self.parent_category.id,
                'category_name':'test_category',
            },
            {
                'category_id': '',
                'category_name':'test_category',
            },
        ]
        self.post_invalid_data = [
            {
                'category_id': self.parent_category.id,
                'category_name': '',
            },
            {
                'category_id': '',
                'category_name': 'duplicate_category',
            },
        ]

    def subtest_post_valid(self, data):
        response = self.client.post(self.test_url, data)
        self.assertRedirects(
            response,
            self.redirect_url,
            302,
            200,
            fetch_redirect_response=True
        )
        parent_id = data.get('category_id')
        parent_id = None if parent_id == '' else parent_id
        self.assertTrue(Category.objects.filter(
                user=self.user,
                parent=parent_id,
                name=data['category_name']
            ).exists()
        )

    def test_post_valid(self):
        for data in self.post_valid_data:
            with self.subTest(data):
                self.subtest_post_valid(data)

    def subtest_post_invalid(self, data):
        category_qty_before = Category.objects.all().count()
        response = self.client.post(self.test_url, data)
        category_qty_after = Category.objects.all().count()
        self.assertRedirects(
            response,
            self.redirect_url,
            302,
            200,
            fetch_redirect_response=True 
        ) 
        self.assertEquals(category_qty_before, category_qty_after)

    def test_post_invalid(self):
        for data in self.post_invalid_data:
            with self.subTest(data):
                self.subtest_post_invalid(data)

    def test_user_fail_test(self):
        category = CategoryFactory(parent=None)
        data = {
            'category_id': category.id,
            'category_name': 'test_category',
        }
        response = self.client.post(self.test_url, data)
        self.assertEquals(response.status_code, 403)
        

class TestCreateIncomeCategory(UserFailTestMixin, BaseViewTestMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:create_income_category')
        cls.redirect_url = reverse('main:categories')
        cls.get_method = False
        cls.view_function = views.CreateIncomeCategory.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

    def setUp(self) -> None:
        super().setUp()
        parent_category = CategoryFactory(user=self.user, parent=None)
        duplicate_category = CategoryFactory(
            user=self.user, 
            parent=parent_category, 
            name='duplicate_category',
            type='I'
        )
        duplicate_category_parent_none = CategoryFactory(
            user=self.user, 
            parent=None, 
            name='duplicate_category',
            type='I'
        )
        self.post_valid_data = [
            {
                'category_id':parent_category.id,
                'category_name':'test_category',
            },
            {
                'category_id': '',
                'category_name':'test_category',
            },
        ]
        self.post_invalid_data = [
            {
                'category_id': parent_category.id,
                'category_name': '',
            },
            {
                'category_id': '',
                'category_name': 'duplicate_category',
            },
        ]

    def subtest_post_valid(self, data):
        response = self.client.post(self.test_url, data)
        self.assertRedirects(
            response,
            self.redirect_url,
            302,
            200,
            fetch_redirect_response=True
        )
        parent_id = data.get('category_id')
        parent_id = None if parent_id == '' else parent_id
        self.assertTrue(Category.objects.filter(
                user=self.user,
                parent=parent_id,
                name=data['category_name']
            ).exists()
        )

    def test_post_valid(self):
        for data in self.post_valid_data:
            with self.subTest(data):
                self.subtest_post_valid(data)

    def subtest_post_invalid(self, data):
        category_qty_before = Category.objects.all().count()
        response = self.client.post(self.test_url, data)
        category_qty_after = Category.objects.all().count()
        self.assertRedirects(
            response,
            self.redirect_url,
            302,
            200,
            fetch_redirect_response=True
        )
        self.assertEquals(category_qty_before, category_qty_after) 

    def test_post_invalid(self):
        for data in self.post_invalid_data:
            with self.subTest(data):
                self.subtest_post_invalid(data)

    def test_user_fail_test(self):
        category = CategoryFactory(parent=None)
        data = {
            'category_id': category.id,
            'category_name': 'test_category',
        }
        response = self.client.post(self.test_url, data)
        self.assertEquals(response.status_code, 403)


class TestDuplicateCategoryData(TransactionTestCase):
    '''
        Testing category create views do not create duplicate categories.    
    '''
    def setUp(self):
        self.user = UserFactoryNoSignal()
        self.client.force_login(self.user)
        self.parent_category = CategoryFactory(user=self.user, parent=None, name='parent')
        self.duplicate_category = CategoryFactory(user=self.user, parent=self.parent_category, name='duplicate')
        self.data = {
            'category_id': self.parent_category.id,
            'category_name': 'duplicate',
        }

    def test_create_expense_category(self):
        response = self.client.post(
            reverse('main:create_expense_category'),
            self.data
        )
        self.assertRedirects(
            response,
            reverse('main:categories'),
            302,
            200,
            fetch_redirect_response=True
        )
        self.assertEquals(Category.objects.all().count(), 2)

    def test_create_income_category(self):
        response = self.client.post(
            reverse('main:create_income_category'),
            self.data
        )
        self.assertRedirects(
            response,
            reverse('main:categories'),
            302,
            200,
            fetch_redirect_response=True
        )
        self.assertEquals(Category.objects.all().count(), 2)


class TestEditExpenseCategory(UserFailTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:edit_expense_category')
        cls.redirect_url = reverse('main:categories')
        cls.get_method = False
        cls.view_function = views.EditExpenseCategory.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

    def setUp(self) -> None:
        super().setUp()
        self.object = CategoryFactory(parent=None, user=self.user)
        self.object_with_parent = CategoryFactory(parent=self.object, user=self.user)
        self.object_protected_category = CategoryFactory(is_protected=True, parent=None, user=self.user)
        self.object_duplicate_category = CategoryFactory(name='duplicate', parent=self.object, user=self.user)
        self.object_duplicate_category_parent_none = CategoryFactory(name='duplicate_parent_none', parent=None, user=self.user)
        self.post_valid_data = [
            {
                'object': self.object,
                'category_id': self.object.id,
                'category_name': 'new category parent none'
            },
            {
                'object': self.object_with_parent,
                'category_id': self.object_with_parent.id,
                'category_name': 'new category'
            }
        ]
        self.post_invalid_data = [
            {
                'category_id': self.object_with_parent.id,
                'category_name': ''
            },
            {
                'category_id': self.object.id,
                'category_name': self.object_duplicate_category_parent_none.name
            },
            {
                'category_id': self.object_with_parent.id,
                'category_name': self.object_duplicate_category.name
            },
        ]

    def test_user_fail_test(self):
        new_user = self.user_factory()
        self.object.user = new_user
        self.object.save()
        response = self.client.post(self.test_url, self.post_valid_data[0])
        self.assertEquals(response.status_code, 404)
       
    def subtest_post_valid(self, data):
        object = data['object']
        self.assertNotEquals(object.name, data['category_name'])
        response = self.client.post(self.test_url, data)
        self.assertRedirects(
            response,
            self.redirect_url,
            302,
            200,
            fetch_redirect_response=True
        )
        object.refresh_from_db()
        self.assertEquals(object.name, data['category_name'])

    def test_post_valid(self):
        for data in self.post_valid_data:
            with self.subTest(data):
                self.subtest_post_valid(data)

    def subtest_post_invalid(self, data):
        response = self.client.post(self.test_url, data)
        self.assertRedirects(
            response,
            self.redirect_url,
            302,
            200,
            fetch_redirect_response=True
        )

    def test_post_invalid(self):
        for data in self.post_invalid_data:
            with self.subTest(data):
                self.subtest_post_invalid(data)

    def test_protected_category(self):
        data = {
            'category_id': self.object_protected_category.id,
            'category_name': 'new category name'
        }
        response = self.client.post(self.test_url, data)
        self.assertEquals(response.status_code, 404)


class TestEditIncomeCategory(UserFailTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:edit_income_category')
        cls.redirect_url = reverse('main:categories')
        cls.get_method = False
        cls.view_function = views.EditIncomeCategory.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal
        cls.get_method = False

    def setUp(self) -> None:
        super().setUp()
        self.object = CategoryFactory(parent=None, user=self.user)
        self.object_with_parent = CategoryFactory(parent=self.object, user=self.user)
        self.object_protected_category = CategoryFactory(is_protected=True, parent=None, user=self.user)
        self.object_duplicate_category = CategoryFactory(name='duplicate', parent=self.object, user=self.user)
        self.object_duplicate_category_parent_none = CategoryFactory(name='duplicate_parent_none', parent=None, user=self.user)
        self.post_data = {
            'category_id': self.object.id,
            'category_name': 'new category parent none'
        }
        self.post_valid_data = [
            {
                'object': self.object,
                'category_id': self.object.id,
                'category_name': 'new category parent none'
            },
            {
                'object': self.object_with_parent,
                'category_id': self.object_with_parent.id,
                'category_name': 'new category'
            }
        ]
        self.post_invalid_data = [
            {
                'category_id': self.object_with_parent.id,
                'category_name': ''
            },
            {
                'category_id': self.object.id,
                'category_name': self.object_duplicate_category_parent_none.name
            },
            {
                'category_id': self.object_with_parent.id,
                'category_name': self.object_duplicate_category.name
            },
        ]

    def test_user_fail_test(self):
        new_user = self.user_factory()
        self.object.user = new_user
        self.object.save()
        response = self.client.post(self.test_url, self.post_valid_data[0])
        self.assertEquals(response.status_code, 404)
       
    def subtest_post_valid(self, data):
        object = data['object']
        self.assertNotEquals(object.name, data['category_name'])
        response = self.client.post(self.test_url, data)
        self.assertRedirects(
            response,
            self.redirect_url,
            302,
            200,
            fetch_redirect_response=True
        )
        object.refresh_from_db()
        self.assertEquals(object.name, data['category_name'])

    def test_post_valid(self):
        for data in self.post_valid_data:
            with self.subTest(data):
                self.subtest_post_valid(data)

    def subtest_post_invalid(self, data):
        response = self.client.post(self.test_url, data)
        self.assertRedirects(
            response,
            self.redirect_url,
            302,
            200,
            fetch_redirect_response=True
        )

    def test_post_invalid(self):
        for data in self.post_invalid_data:
            with self.subTest(data):
                self.subtest_post_invalid(data)

    def test_protected_category(self):
        data = {
            'category_id': self.object_protected_category.id,
            'category_name': 'new category name'
        }
        response = self.client.post(self.test_url, data)
        self.assertEquals(response.status_code, 404)


class TestDeleteExpenseCategory(UserFailTestMixin, BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = ''
        cls.redirect_url = reverse('main:categories')
        cls.view_function = views.DeleteExpenseCategory.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal
        cls.get_method = False
        
    def setUp(self) -> None:
        super().setUp()
        self.object = CategoryFactory(user=self.user, parent=None)
        self.test_url = reverse("main:delete_expense_category", kwargs={'pk':self.object.id})
        self.post_data = {}

    def test_post(self):
        self.assertTrue(Category.objects.all().exists())
        response = self.client.post(self.test_url, self.post_data)
        self.assertRedirects(
            response,
            self.redirect_url,
            302,
            200,
            fetch_redirect_response=True,
        )
        self.assertFalse(Category.objects.all().exists())

    def test_protected_category(self):
        self.object.is_protected = True
        self.object.save()
        data = {}
        response = self.client.post(self.test_url, data)
        self.assertEquals(response.status_code, 404)
        self.assertTrue(Category.objects.filter(id=self.object.id).exists())


class TestDeleteIncomeCategory(UserFailTestMixin, BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = ''
        cls.redirect_url = reverse('main:categories')
        cls.view_function = views.DeleteIncomeCategory.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal
        cls.get_method = False
        
    def setUp(self) -> None:
        super().setUp()
        self.object = CategoryFactory(user=self.user, parent=None)
        self.test_url = reverse('main:delete_income_category', kwargs={'pk': self.object.id})
        self.post_data = {}

    def test_post(self):
        self.assertTrue(Category.objects.all().exists())
        response = self.client.post(self.test_url, self.post_data)
        self.assertRedirects(
            response,
            self.redirect_url,
            302,
            200,
            fetch_redirect_response=True,
        )
        self.assertFalse(Category.objects.all().exists())

    def test_protected_category(self):
        self.object.is_protected = True
        self.object.save()
        response = self.client.post(self.test_url, self.post_data)
        self.assertEquals(response.status_code, 404)
        self.assertTrue(Category.objects.filter(id=self.object.id).exists())


class TestWorthView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:worth')
        cls.context_list = ['stats', 'currency_details', 'grand_total']
        cls.template = 'main/worth.html'
        cls.view_function = views.WorthView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal
    
    def setUp(self):
        super().setUp()
        self.user.user_preferences = UserPreferencesFactory(user=self.user)


class TestTransactionsView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:transactions')
        cls.context_list = ['transactions', 'paginator']
        cls.template = 'main/transactions.html'
        cls.view_function = views.TransactionsView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal


class TestTransactionsAllArchiveView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:transactions_all_archive')
        cls.context_list = ['object_list', 'date_list', 'table_template', 'transactions']
        cls.template = 'main/group_table_paginator.html'
        cls.view_function = views.TransactionsAllArchiveView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal


class TestTransactionsYearArchiveView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:transactions_year_archive', kwargs={'year': 2022})
        cls.context_list = ['object_list', 'date_list', 'table_template', 'transactions']
        cls.template = 'main/group_table_paginator.html'
        cls.view_function = views.TransactionsYearArchiveView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal


class TestTransactionsMonthArchiveView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:transactions_month_archive', kwargs={'year': 2022, 'month': 1})
        cls.context_list = ['object_list', 'date_list', 'table_template', 'transactions']
        cls.template = 'main/group_table_paginator.html'
        cls.view_function = views.TransactionsMonthArchiveView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal


class TestTransactionsWeekArchiveView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:transactions_week_archive', kwargs={'year': 2022, 'week': 1})
        cls.context_list = ['object_list', 'date_list', 'table_template', 'transactions']
        cls.template = 'main/group_table_paginator.html'
        cls.view_function = views.TransactionsWeekArchiveView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal


class TestTransactionsDayArchiveView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:transactions_day_archive', kwargs={'year': 2022, 'month': 1, 'day': 1})
        cls.context_list = ['object_list', 'date_list', 'table_template', 'transactions']
        cls.template = 'main/group_table_paginator.html'
        cls.view_function = views.TransactionsDayArchiveView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal


class TestEditTransactionView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.success_url = reverse('main:main')
        cls.model = Transaction
        cls.model_factory = AccountTransactionFactory
        cls.user_factory = UserFactoryNoSignal
        cls.login_required = True
        cls.context_list = ['form']
        cls.template = 'main/transaction_edit.html'
        cls.get_method = True
        cls.view_function = views.EditTransactionView.as_view()
        cls.test_url = ''

    def setUp(self) -> None:
        super().setUp()
        self.account1 = AccountFactory(user=self.user, balance=10)
        self.account2 = AccountFactory(user=self.user, balance=20)
        expense_category1 = CategoryFactory(user=self.user, parent=None, type='E', is_transfer=False)
        self.object = AccountTransactionFactory(
            name='test_transfer', 
            content_object=self.account1, 
            category=expense_category1,
            amount=1,
            date=date(2020, 5, 17),
            type='E',
        )
        self.test_url = reverse('main:edit_transaction', kwargs={'pk': self.object.id})

    def test_expense_post_success(self):
        expense_category2 = CategoryFactory(user=self.user, parent=None, type='E', is_transfer=False)
        
        data = {
            'name': 'test_transfer_edit',
            'object_id': self.account2.id,
            'amount': 2,
            'category': expense_category2.id,
            'date': date(2020, 5, 18),
            }
        response = self.client.post(self.test_url, data)
        self.assertRedirects(response, self.success_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.object.refresh_from_db()
        for key, value in data.items():
            if isinstance(getattr(self.object, key), models.Model):
                self.assertEquals(getattr(self.object, key).id, value)
            else:
                self.assertEquals(getattr(self.object, key), value)
        self.account1.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEquals(self.account1.balance, 11)
        self.assertEquals(self.account2.balance, 18)
    
    def test_expense_post_failure(self):
        expense_category2 = CategoryFactory(user=self.user, parent=None, type='E')
        
        data = {
            'name': 'test_transfer_edit',
            'object_id': self.account2.id,
            'amount': 'abc',
            'category': expense_category2.id,
            'date': date(2020, 5, 18),
            }
        pre_update_values = self.object.__dict__
        response = self.client.post(self.test_url, data)
        self.assertEquals(response.status_code, 200)
        self.object.refresh_from_db()
        post_update_values = self.object.__dict__
        self.assertEquals(pre_update_values, post_update_values)
        self.account1.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEquals(self.account1.balance, 10)
        self.assertEquals(self.account2.balance, 20)
    
    def test_income_post_success(self):
        self.object.type = 'I'
        self.object.save()
        income_category2 = CategoryFactory(user=self.user, parent=None, type='I', is_transfer=False)
        
        data = {
            'name': 'test_transfer_edit',
            'object_id': self.account2.id,
            'amount': 2,
            'category': income_category2.id,
            'date': date(2020, 5, 18),
            }
        response = self.client.post(self.test_url, data)
        self.assertRedirects(response, self.success_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.object.refresh_from_db()
        for key, value in data.items():
            if isinstance(getattr(self.object, key), models.Model):
                self.assertEquals(getattr(self.object, key).id, value)
            else:
                self.assertEquals(getattr(self.object, key), value)
        self.account1.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEquals(self.account1.balance, 9)
        self.assertEquals(self.account2.balance, 22)

    def test_income_post_failure(self):
        income_category2 = CategoryFactory(user=self.user, parent=None, type='I')
        
        data = {
            'name': 'test_transfer_edit',
            'object_id': self.account2.id,
            'amount': 'abc',
            'category': income_category2.id,
            'date': date(2020, 5, 18),
            }
        pre_update_values = self.object.__dict__
        response = self.client.post(self.test_url, data)
        self.assertEquals(response.status_code, 200)
        self.object.refresh_from_db()
        post_update_values = self.object.__dict__
        self.assertEquals(pre_update_values, post_update_values)
        self.account1.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEquals(self.account1.balance, 10)
        self.assertEquals(self.account2.balance, 20)


class TestDeleteTransactionView(UserFailTestMixin, TestDeleteViewMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = Transaction
        cls.model_factory = AccountTransactionFactory
        cls.test_url_pattern = '/transactions/<pk>/delete' 
        cls.success_url = reverse('main:main')
        cls.context_list = []
        cls.get_method = False
        cls.post_data = {}
        cls.view_function = views.DeleteTransactionView.as_view()  # Add .as_view()
        cls.login_required = True  # bool
        cls.user_factory = UserFactoryNoSignal

    def test_user_fail_test(self):
        non_user_account = AccountFactory()
        non_user_object = AccountTransactionFactory(content_object=non_user_account)
        test_url=f'/transactions/{non_user_object.id}/delete'
        response = self.client.post(test_url, self.post_data)
        self.assertIn(response.status_code, (403, 404))

    def set_object(self):
        self.user_account = AccountFactory(user=self.user, balance=10)
        self.object = AccountTransactionFactory(content_object=self.user_account, amount=1, type='E')

    def test_post_expense_success(self):
        self.assertTrue(self.model.objects.all().exists())
        response = self.client.post(self.test_url, self.post_data)
        self.assertRedirects(
            response,
            self.success_url,
            302,
            200,
            fetch_redirect_response=True,
        )
        self.assertFalse(self.model.objects.all().exists())
        self.user_account.refresh_from_db()
        self.assertEquals(self.user_account.balance, 11)

    def test_post_income_success(self):
        self.object.type = 'I'
        self.object.save()
        self.assertTrue(self.model.objects.all().exists())
        response = self.client.post(self.test_url, self.post_data)
        self.assertRedirects(
            response,
            self.success_url,
            302,
            200,
            fetch_redirect_response=True,
        )
        self.assertFalse(self.model.objects.all().exists())
        self.user_account.refresh_from_db()
        self.assertEquals(self.user_account.balance, 9)

class TestDeleteTransferView(UserFailTestMixin, TestDeleteViewMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = Transfer
        cls.model_factory = TransferFactory
        cls.object_context_name = 'object'
        cls.context_list = []
        cls.test_url_pattern = '/transfers/<pk>/delete'
        cls.success_url = reverse('main:transfer')
        cls.get_method = False
        cls.post_data = None
        cls.view_function = views.DeleteTransferView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

    def set_object(self):
        self.object = self.model_factory.create(user=self.user)

    def test_post_success(self):
        self.assertTrue(Transaction.objects.exists())
        self.assertTrue(Transfer.objects.exists())
        response = self.client.post(self.test_url, self.post_data)
        self.assertRedirects(
            response,
            self.success_url,
            302,
            200,
            fetch_redirect_response=True,
        )
        self.assertFalse(Transfer.objects.exists())
        self.assertFalse(Transaction.objects.exists())

class TestTransfersView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:transfers')
        cls.context_list = ['transfers', 'paginator']
        cls.template = 'main/transfers.html'
        cls.view_function = views.TransfersView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

class TestTransfersYearArchiveView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:transfers_year_archive', kwargs={'year': 2022})
        cls.context_list = ['object_list', 'date_list', 'table_template', 'transfers']
        cls.template = 'main/group_table_paginator.html'
        cls.view_function = views.TransfersYearArchiveView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

class TestTransfersMonthArchiveView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:transfers_month_archive', kwargs={'year': 2022, 'month': 1})
        cls.context_list = ['object_list', 'date_list', 'table_template', 'transfers']
        cls.template = 'main/group_table_paginator.html'
        cls.view_function = views.TransfersMonthArchiveView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

class TestTransfersWeekArchiveView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:transfers_week_archive', kwargs={'year': 2022, 'week': 1})
        cls.context_list = ['object_list', 'date_list', 'table_template', 'transfers']
        cls.template = 'main/group_table_paginator.html'
        cls.view_function = views.TransfersWeekArchiveView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

class TestTransfersDayArchiveView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:transfers_day_archive', kwargs={'year': 2022, 'month': 1, 'day': 1})
        cls.context_list = ['object_list', 'date_list', 'table_template', 'transfers']
        cls.template = 'main/group_table_paginator.html'
        cls.view_function = views.TransfersDayArchiveView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

class TestTransfersAllArchiveView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:transfers_all_archive')
        cls.context_list = ['object_list', 'date_list', 'table_template', 'transfers']
        cls.template = 'main/group_table_paginator.html'
        cls.view_function = views.TransfersAllArchiveView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

class TestEditTransferView(TestUpdateViewMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url_pattern = '/transfers/<pk>/edit' 
        cls.success_url = reverse('main:main')
        cls.model = Transfer
        
        cls.model_factory = TransferFactory
        cls.user_factory = UserFactoryNoSignal
        cls.context_list = ['form']
        cls.template = 'main/transfer_edit.html'
        cls.view_function = views.EditTransferView.as_view()
        cls.login_required = True
    
    def setUp(self) -> None:
        super().setUp()
        self.test_account1 = AccountFactory(user=self.user)
        self.test_account2 = AccountFactory(user=self.user)
        self.valid_data = [{
            'from_account': self.test_account1.id,
            'to_account': self.test_account2.id,
            'from_amount': 10,
            'to_amount': 20,
            'date': date(2001,1,1)
        }]
        self.invalid_data = [{
            'from_account': 'invalid value',
            'to_account': self.test_account2.id,
            'from_amount': 'invalid value',
            'to_amount': 20,
            'date': date(2001,1,1)
        }]

    def set_object(self):
        self.object = self.model_factory.create(user=self.user)

    def subtest_post_success(self, data):
        response = self.client.post(self.test_url, data=data)
        self.assertRedirects(response, self.success_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.object.refresh_from_db()
        self.assertEquals(Transfer.objects.count(), 1)
        self.assertEquals(self.object.from_transaction.content_object, self.test_account1)
        self.assertEquals(self.object.to_transaction.content_object, self.test_account2)

    def test_post_success(self):
        for data in self.valid_data:
            with self.subTest(data=data):
                self.subtest_post_success(data)


class TestInsOutsView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:ins_outs')
        cls.context_list = ["date", "expense_stats", "income_stats", "comparison_stats", 'report', 'total']
        cls.template = 'main/ins_outs.html'
        cls.view_function = views.InsOutsView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

    def test_get(self):
        UserPreferencesFactory(user=self.user)
        super().test_get()

class TestInsOutsAllArchiveView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:ins_outs_all_archive')
        cls.context_list = ["expense_stats", "income_stats", "comparison_stats", 'report', 'total']
        cls.template = 'main/group_report_chart_script.html'
        cls.view_function = views.InsOutsAllArchiveView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

    def test_get(self):
        UserPreferencesFactory(user=self.user)
        super().test_get()

class TestInsOutsYearArchiveView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:ins_outs_year_archive', kwargs={'year': 2001})
        cls.context_list = ["expense_stats", "income_stats", "comparison_stats", 'report', 'total']
        cls.template = 'main/group_report_chart_script.html'
        cls.view_function = views.InsOutsYearArchiveView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

    def test_get(self):
        UserPreferencesFactory(user=self.user)
        super().test_get()


class TestInsOutsMonthArchiveView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:ins_outs_month_archive', kwargs={'year': 2001, 'month': 1})
        cls.context_list = ["expense_stats", "income_stats", "comparison_stats", 'report', 'total']
        cls.template = 'main/group_report_chart_script.html'
        cls.view_function = views.InsOutsMonthArchiveView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

    def test_get(self):
        UserPreferencesFactory(user=self.user)
        super().test_get()


class TestInsOutsWeekArchiveView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:ins_outs_week_archive', kwargs={'year': 2001, 'week': 1})
        cls.context_list = ["expense_stats", "income_stats", "comparison_stats", 'report', 'total']
        cls.template = 'main/group_report_chart_script.html'
        cls.view_function = views.InsOutsWeekArchiveView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

    def test_get(self):
        UserPreferencesFactory(user=self.user)
        super().test_get()


class TestInsOutsDayArchiveView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:ins_outs_day_archive', kwargs={'year': 2001, 'month': 1, 'day': 1})
        cls.context_list = ["expense_stats", "income_stats", "comparison_stats", 'report', 'total']
        cls.template = 'main/group_report_chart_script.html'
        cls.view_function = views.InsOutsDayArchiveView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

    def test_get(self):
        UserPreferencesFactory(user=self.user)
        super().test_get()


class TestCategoryAllArchiveView(BaseViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.context_list = ['transactions']
        cls.template = 'main/category_detail.html'
        cls.view_function = views.CategoryAllArchiveView.as_view()
        cls.login_required = True
        cls.user_factory = UserFactoryNoSignal

    def setUp(self) -> None:
        self.user = self.get_user()
        self.object = CategoryFactory(user=self.user, parent=None)
        self.test_url = reverse('main:category_all_archive', kwargs={'pk': self.object.id})
        if self.login_required:
            self.client.force_login(self.user)

    def test_get_ajax(self):
        test_url = self.test_url + '?ajax=1'
        response = self.client.get(test_url)      
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')