from decimal import Decimal
import json
import factory
from requests import request
from .factories import CategoryFactory, TransactionFactory, TransferFactory, UserFactoryNoSignal
from .cbv_test_mixins import (
    TestCreateViewMixin,
    TestListViewMixin,
    TestUpdateViewMixin,
)
from main.forms import TransferForm, ExpenseInputForm, IncomeInputForm
from main.models import Account, Category, Loan, Transaction, Transfer, User
from .factories import AccountFactory, CurrencyFactory, LoanFactory
from django.urls import reverse, resolve
from django.db import models
from django.db.models import signals
from django.test import TestCase
from django.http import JsonResponse
from main import views
from django.db import models
from datetime import date


class TestCreateAccountView(TestCreateViewMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:create_account')
        cls.success_url = reverse('main:index')
        cls.model = Account
        cls.context_list = ('form', )
        cls.template = 'main/create_account.html'
        cls.view_function = views.CreateAccountView.as_view()
        cls.login_required = True

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
                'name': 'sample_account',
                'balance': Decimal(-32.00),
                'currency': currency.id,
            },
        ]
        self.invalid_data = [
            {
                'name': 'sample_account',
                'balance': 'abc', # balance must be a number.
                'currency': currency.id,
            }
        ]    
    
    def get_user(self):
        user = UserFactoryNoSignal()
        return user

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
        # test object's user is self.user
        self.assertEquals(self.user, self.valid_object.user)
        for key, value in data.items():
            if isinstance(getattr(self.valid_object, key), models.Model):
                self.assertEquals(getattr(self.valid_object, key).id, value)
            else:
                self.assertEquals(getattr(self.valid_object, key), value)


class TestCreateLoanView(TestCreateViewMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = reverse('main:create_loan')
        cls.success_url = reverse('main:index')
        cls.model = Loan
        cls.context_list = ('form', )
        cls.template = 'main/create_loan.html'
        cls.view_function = views.CreateLoanView.as_view()
        cls.login_required = True

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
                'name': 'sample_loan',
                'balance': Decimal(-32.00),
                'currency': currency.id,
            },
        ]
        self.invalid_data = [
            {
                'name': 'sample_loan',
                'balance': 'abc', # balance must be a number.
                'currency': currency.id,
            }
        ]    
    
    def get_user(self):
        user = UserFactoryNoSignal()
        return user

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

    def get_user(self):
        user = UserFactoryNoSignal()
        return user

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


class TestUpdateAccountView(TestUpdateViewMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url_pattern = '/accounts/<pk>/edit'
        cls.success_url = reverse('main:index')
        cls.model = Account
        cls.context_list = ('form', )
        cls.template = 'main/account_update.html'
        cls.view_function = views.EditAccountView.as_view()
        cls.login_required = True
        cls.model_factory = AccountFactory

    def setUp(self) -> None:
        super().setUp()
        currency = CurrencyFactory()
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

    def get_user(self):
        user = UserFactoryNoSignal()
        return user

    def set_object(self):
        super().set_object()
        self.object.user = self.user
        self.object.save()
    

class TestIndexView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_url = reverse('main:index')
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
        cls.template = 'main/index.html'
        cls.view_function = views.index

    def setUp(self) -> None:
        self.user = self.get_user()
        self.client.force_login(self.user)

    def get_user(self):
        user = UserFactoryNoSignal(username='testuser')
        return user

    def test_unauthenticated_access(self):
        '''
            Tests unauthenticated access in case view has LoginRequired mixin.
        '''
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertRedirects(response, '/login?next=/')

    def test_get(self):    
        '''
            Tests get request response has status 200 and 
            response context has expected keys.
        ''' 
        response = self.client.get(self.test_url)
        self.assertEquals(response.status_code, 200)
        # test template
        self.assertTemplateUsed(response, self.template)
        # test context
        if self.context_list:
            for item in self.context_list:
                self.assertIn(item, response.context.keys())

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
        TransactionFactory.create_batch(
            10, 
            account__user=self.user, 
            category__is_transfer=False
        )
        TransactionFactory.create_batch(
            10, 
            account__user=self.user, 
            category__is_transfer=True
        )
        TransactionFactory.create_batch(10)
        transactions = (
            Transaction.objects.filter(account__user=self.user)
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
            reverse('main:index'), 
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
            transfer_obj.from_transaction.account.id,
            msg="From account value not matching",
        )
        self.assertEquals(
            data['from_amount'], 
            transfer_obj.from_transaction.amount,
            msg="From amount value not matching",
        )
        self.assertEquals(
            data['to_account'], 
            transfer_obj.to_transaction.account.id,
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
            'account': account.id,
            'amount': 12,
            'category': category.id,
            'date': date.today(),
            'type': 'E'
        }
        response = self.client.post(self.test_url, data)
        self.assertRedirects(
            response, 
            reverse('main:index'), 
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
            data['account'], 
            transaction_obj.account.id,
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
            'account': account.id,
            'amount': 12,
            'category': category.id,
            'date': date.today(),
            'type': 'I'
        }
        response = self.client.post(self.test_url, data)
        self.assertRedirects(
            response, 
            reverse('main:index'), 
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
            data['account'], 
            transaction_obj.account.id,
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

    def test_view_function(self):
        '''
            Tests url resolves to view function.
        '''
        match = resolve(self.test_url)
        self.assertEquals(self.view_function.__name__, match.func.__name__)


class TestTransactionNameAutocomplete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_url = reverse('main:transaction_name_autocomplete')
        cls.view_function = views.transaction_name_autocomplete

    def setUp(self) -> None:
        self.user = self.get_user()
        self.client.force_login(self.user)

    def get_user(self):
        user = UserFactoryNoSignal(username='testuser')
        return user

    def test_unauthenticated_access(self):
        '''
            Tests unauthenticated access.
        '''
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertRedirects(response, '/login?next=/autocomplete/transaction_name')

    def test_get(self):
        for i in range(6):
            TransactionFactory(name=f'match_E{i}', type='E', account__user=self.user)
        for i in range(5):
            TransactionFactory(name=f'fail{i}', type='E', account__user=self.user)
        for i in range(7):
            TransactionFactory(name=f'match_I{i}', type='I', account__user=self.user)
        for i in range(5):
            TransactionFactory(name=f'fail{i}', type='I', account__user=self.user)
        for i in range(5):
            TransactionFactory(name=f'match{i}', type='E')
        for i in range(5):
            TransactionFactory(name=f'fail{i}', type='E')
        for i in range(5):
            TransactionFactory(name=f'match{i}', type='I')
        for i in range(5):
            TransactionFactory(name=f'fail{i}', type='I')
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

    def test_view_function(self):
        '''
            Tests url resolves to view function.
        '''
        match = resolve(self.test_url)
        self.assertEquals(self.view_function.__name__, match.func.__name__)


class TestLoginView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_url = reverse('main:login')
        cls.template = 'main/login.html'
        cls.view_function = views.LoginView.as_view()
        cls.success_url = reverse('main:index')
        cls.next_url = reverse('main:accounts')

    def setUp(self) -> None:
        self.password = 'testpassword'
        self.user = self.get_user()

    def get_user(self):
        user = UserFactoryNoSignal(username='testuser')
        user.set_password(self.password)
        user.save()
        return user

    def test_get(self):    
        '''
            Tests get request response has status 200 and 
            response context has expected keys.
        ''' 
        response = self.client.get(self.test_url)
        self.assertEquals(response.status_code, 200)
        # test template
        self.assertTemplateUsed(response, self.template)
        
    def test_post(self):
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

    def test_view_function(self):
        '''
            Tests url resolves to view function.
        '''
        match = resolve(self.test_url)
        self.assertEquals(self.view_function.__name__, match.func.__name__)

class TestRegisterView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_url = reverse('main:register')
        cls.template = 'main/register.html'
        cls.view_function = views.RegisterView.as_view()
        cls.success_url = reverse('main:index')
        cls.error_url = reverse('main:register')

    def setUp(self) -> None:
        self.user = self.get_user()

    def get_user(self):
        user = UserFactoryNoSignal(username='testuser')
        return user

    def test_get(self):    
        '''
            Tests get request response has status 200 and 
            response context has expected keys.
        ''' 
        response = self.client.get(self.test_url)
        self.assertEquals(response.status_code, 200)
        # test template
        self.assertTemplateUsed(response, self.template)
        
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
    
    def test_view_function(self):
        '''
            Tests url resolves to view function.
        '''
        match = resolve(self.test_url)
        self.assertEquals(self.view_function.__name__, match.func.__name__)

        
# class TestTest(TestCase):
#     def test_func(self):
#         transfer = TransferFactory(from_transaction__category__parent__parent=None, to_transaction__category__parent__parent=None)
#         for key, value in transfer.__dict__.items():
#             print(key, ':', value)
#         cats = Category.objects.all()
#         for cat in cats:
#             print(cat.name, cat.parent)