from typing import List
from main.forms import (
    ExpenseInputForm,
    IncomeInputForm,
    TransferForm,
    PayLoanForm,
)
from main.models import Account, Category
from main.tests.factories import UserFactoryNoSignal, CategoryFactory, AccountFactory
from unittest.mock import patch
import datetime

from django.test.testcases import TestCase, SimpleTestCase
from django.db.models.query import BaseIterable

class TestForms(TestCase):
    def test_expense_input_form(self):
        data = {
            'name': 'test_name',
            'account': '1',
            'amount': '10',
            'category': '1',
            'date': datetime.date(2022,2,2),
            'type': 'E'
        }
        form = ExpenseInputForm(user=1, data=data)
        self.assertEquals(
            form.errors['account'][0],
            'Select a valid choice. That choice is not one of the available choices.'
        )
        self.assertEquals(
            form.errors['category'][0],
            'Select a valid choice. That choice is not one of the available choices.'
        )
        self.assertEquals(form['name'].value(), data['name'])
        self.assertEquals(form['amount'].value(), data['amount'])
        self.assertEquals(form['date'].value(), data['date'])
        self.assertEquals(form['type'].value(), data['type'])