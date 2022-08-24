from codecs import ascii_encode
from unicodedata import category
from main.forms import (
    ExpenseInputForm,
    IncomeInputForm,
    TransferForm,
    PayLoanForm,
)
from main.tests.factories import (
    UserFactoryNoSignal,
    AccountFactory,
    CategoryFactory,
    LoanFactory
)
import datetime
from django.test.testcases import TestCase

class TestForms(TestCase):
    def setUp(self):
        self.user = UserFactoryNoSignal()
        self.valid_account = AccountFactory(user=self.user)
        self.invalid_account = AccountFactory()
        self.valid_expense_category = CategoryFactory(user=self.user, type='E', parent=None)
        self.valid_income_category = CategoryFactory(user=self.user, type='I', parent=None)
        self.invalid_category = CategoryFactory(parent=None)

    def test_expense_input_form_with_valid_data(self):        
        data = {
            'name': 'test_name',
            'account': self.valid_account.id,
            'amount': '10',
            'category': self.valid_expense_category.id,
            'date': datetime.date(2022,2,2),
            'type': 'E'
        }
        form = ExpenseInputForm(user=self.user, data=data)
        for key, value in data.items():
            self.assertEquals(form[key].value(), value)

    def test_expense_input_form_with_invalid_data(self):
        data = {
            'name': '',
            'account': self.invalid_account.id,
            'amount': 'abc',
            'category': self.invalid_category.id,
            'date': 'invalid_date',
            'type': 'invalid type'
        }
        form = ExpenseInputForm(user=self.user, data=data)
        for key, value in data.items():
            self.assertIn(key, form.errors)
            

    def test_income_input_form_with_valid_data(self):        
        data = {
            'name': 'test_name',
            'account': self.valid_account.id,
            'amount': '10',
            'category': self.valid_income_category.id,
            'date': datetime.date(2022,2,2),
            'type': 'I'
        }
        form = IncomeInputForm(user=self.user, data=data)
        for key, value in data.items():
            self.assertEquals(form[key].value(), value)

    def test_income_input_form_with_invalid_data(self):
        data = {
            'name': '',
            'account': self.invalid_account.id,
            'amount': 'abc',
            'category': self.invalid_category.id,
            'date': 'invalid_date',
            'type': 'invalid type'
        }
        form = IncomeInputForm(user=self.user, data=data)
        for key, value in data.items():
            self.assertIn(key, form.errors)
