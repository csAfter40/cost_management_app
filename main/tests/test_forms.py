from unicodedata import category
from main.forms import (
    ExpenseInputForm,
    IncomeInputForm,
    SetupForm,
    TransferForm,
    PayLoanForm,
    PayCreditCardForm,
    LoanDetailPaymentForm,
    EditTransactionForm,
    CreateCreditCardForm
)
from main.models import UserPreferences
from main.tests.factories import (
    AccountTransactionFactory,
    CurrencyFactory,
    TransactionFactory,
    UserFactoryNoSignal,
    AccountFactory,
    CategoryFactory,
    LoanFactory,
    CreditCardFactory,
    UserPreferencesFactory,
)
import datetime
from django.test.testcases import TestCase


class TestForms(TestCase):
    def setUp(self):
        self.user = UserFactoryNoSignal()
        self.valid_account = AccountFactory(user=self.user)
        self.valid_card = CreditCardFactory(user=self.user)
        self.invalid_account = AccountFactory()
        self.invalid_card = CreditCardFactory()
        self.valid_expense_category = CategoryFactory(
            user=self.user, type="E", parent=None
        )
        self.valid_income_category = CategoryFactory(
            user=self.user, type="I", parent=None
        )
        self.invalid_category = CategoryFactory(parent=None)

    def test_expense_input_form_with_valid_account_data(self):
        data = {
            "expense_asset": "account",
            "name": "test_name",
            "content_object": self.valid_account.id,
            "amount": "10",
            "installments": None,
            "category": self.valid_expense_category.id,
            "date": datetime.date(2022, 2, 2),
            "type": "E",
        }
        form = ExpenseInputForm(user=self.user, data=data)
        del data["expense_asset"]
        for key, value in data.items():
            self.assertEquals(form[key].value(), value)
    
    def test_expense_input_form_with_invalid_data(self):
        data = {
            "expense_asset": "invalid asset",
            "name": "",
            "content_object": "10000",
            "amount": "invalid amount",
            "installments": 55,
            "category": self.invalid_category.id,
            "date": "invalid date",
            "type": "invalid type",
        }
        form = ExpenseInputForm(user=self.user, data=data)
        del data["expense_asset"]
        for key, value in data.items():
            self.assertIn(key, form.errors)

    def test_expense_input_form_with_valid_card_data_no_installments(self):
        data = {
            "expense_asset": "card",
            "name": "test_name",
            "content_object": self.valid_card.id,
            "amount": "10",
            "installments": None,
            "category": self.valid_expense_category.id,
            "date": datetime.date(2022, 2, 2),
            "type": "E",
        }
        form = ExpenseInputForm(user=self.user, data=data)
        del data["expense_asset"]
        for key, value in data.items():
            self.assertEquals(form[key].value(), value)


    def test_expense_input_form_with_valid_card_data_with_installments(self):
        data = {
            "expense_asset": "card",
            "name": "test_name",
            "content_object": self.valid_card.id,
            "amount": "10",
            "installments": 10,
            "category": self.valid_expense_category.id,
            "date": datetime.date(2022, 2, 2),
            "type": "E",
        }
        form = ExpenseInputForm(user=self.user, data=data)
        del data["expense_asset"]
        for key, value in data.items():
            self.assertEquals(form[key].value(), value)

    def test_income_input_form_with_valid_account_data(self):
        data = {
            "income_asset": "account",
            "name": "test_name",
            "content_object": self.valid_account.id,
            "amount": "10",
            "category": self.valid_income_category.id,
            "date": datetime.date(2022, 2, 2),
            "type": "I",
        }
        form = IncomeInputForm(user=self.user, data=data)
        for key, value in data.items():
            self.assertEquals(form[key].value(), value)

    def test_income_input_form_with_valid_card_data(self):
        data = {
            "income_asset": "account",
            "name": "test_name",
            "content_object": self.valid_card.id,
            "amount": "10",
            "category": self.valid_income_category.id,
            "date": datetime.date(2022, 2, 2),
            "type": "I",
        }
        form = IncomeInputForm(user=self.user, data=data)
        for key, value in data.items():
            self.assertEquals(form[key].value(), value)

    def test_income_input_form_with_invalid_data(self):
        data = {
            "name": "",
            "content_object": self.invalid_account.id,
            "amount": "abc",
            "category": self.invalid_category.id,
            "date": "invalid_date",
            "type": "invalid type",
        }
        form = IncomeInputForm(user=self.user, data=data)
        for key, value in data.items():
            self.assertIn(key, form.errors)

    def test_transfer_form_with_valid_data(self):
        to_account = AccountFactory(user=self.user)
        data = {
            "from_account": self.valid_account.id,
            "to_account": to_account.id,
            "from_amount": 10,
            "to_amount": 10,
            "date": datetime.date(2022, 2, 2),
        }
        form = TransferForm(user=self.user, data=data)
        for key, value in data.items():
            self.assertEquals(form[key].value(), value)

    def test_transfer_form_with_invalid_data(self):
        invalid_to_account = AccountFactory()
        data = {
            "from_account": self.invalid_account.id,
            "to_account": invalid_to_account.id,
            "from_amount": "invalid amount",
            "to_amount": "invalid amount",
            "date": "invalid date",
        }
        form = TransferForm(user=self.user, data=data)
        for key, value in data.items():
            self.assertIn(key, form.errors)

    def test_transfer_form_from_account_equals_to_account(self):
        data = {
            "from_account": self.valid_account.id,
            "to_account": self.valid_account.id,
            "from_amount": 10,
            "to_amount": 10,
            "date": datetime.date(2022, 2, 2),
        }
        form = TransferForm(user=self.user, data=data)
        self.assertIn(
            "From account and To account can not have same value.",
            form.errors["__all__"],
        )

    def test_pay_credit_card_form_with_valid_data(self):
        currency = CurrencyFactory()
        valid_card = CreditCardFactory(user=self.user, currency=currency)
        valid_account = AccountFactory(user=self.user, currency=currency)
        data = {
            "account": valid_account.id,
            "card": valid_card.id,
            "amount": 10,
            "date": datetime.date(2022, 2, 2),
        }
        form = PayCreditCardForm(user=self.user, data=data)
        for key, value in data.items():
            self.assertEquals(form[key].value(), value)

    def test_pay_credit_card_form_with_invalid_data(self):
        currency = CurrencyFactory()
        invalid_card = CreditCardFactory(currency=currency)
        invalid_account = AccountFactory(currency=currency)
        data = {
            "account": invalid_account.id,
            "card": invalid_card.id,
            "amount": "invalid amount",
            "date": "invalid date",
        }
        form = PayCreditCardForm(user=self.user, data=data)
        for key, value in data.items():
            self.assertIn(key, form.errors)

    def test_pay_credit_card_form_account_and_card_currencies_not_matching(self):
        card_currency = CurrencyFactory()
        account_currency = CurrencyFactory()
        valid_card = CreditCardFactory(user=self.user, currency=card_currency)
        valid_account = AccountFactory(user=self.user, currency=account_currency)
        data = {
            "account": valid_account.id,
            "card": valid_card.id,
            "amount": 10,
            "date": datetime.date(2022, 2, 2),
        }
        form = PayCreditCardForm(user=self.user, data=data)
        self.assertIn(
            "Account and credit card currencies can not be different.", form.errors["__all__"]
        )

    def test_pay_credit_card_form_with_invalid_account(self):
        currency = CurrencyFactory()
        valid_card = CreditCardFactory(user=self.user, currency=currency)
        invalid_account = AccountFactory(currency=currency)
        data = {
            "account": invalid_account.id,
            "card": valid_card.id,
            "amount": 10,
            "date": datetime.date(2022, 2, 2),
        }
        form = PayCreditCardForm(user=self.user, data=data)
        self.assertIn("Invalid account or credit card data.", form.errors["__all__"])

    def test_pay_credit_form_with_invalid_account(self):
        currency = CurrencyFactory()
        invalid_card = CreditCardFactory(currency=currency)
        valid_account = AccountFactory(user=self.user, currency=currency)
        data = {
            "account": valid_account.id,
            "card": invalid_card.id,
            "amount": 10,
            "date": datetime.date(2022, 2, 2),
        }
        form = PayCreditCardForm(user=self.user, data=data)
        self.assertIn("Invalid account or credit card data.", form.errors["__all__"])
        
    def test_pay_loan_form_with_valid_data(self):
        currency = CurrencyFactory()
        valid_loan = LoanFactory(user=self.user, currency=currency)
        valid_account = AccountFactory(user=self.user, currency=currency)
        data = {
            "account": valid_account.id,
            "loan": valid_loan.id,
            "amount": 10,
            "date": datetime.date(2022, 2, 2),
        }
        form = PayLoanForm(user=self.user, data=data)
        for key, value in data.items():
            self.assertEquals(form[key].value(), value)

    def test_pay_loan_form_with_invalid_data(self):
        currency = CurrencyFactory()
        invalid_loan = LoanFactory(currency=currency)
        invalid_account = AccountFactory(currency=currency)
        data = {
            "account": invalid_account.id,
            "loan": invalid_loan.id,
            "amount": "invalid amount",
            "date": "invalid date",
        }
        form = PayLoanForm(user=self.user, data=data)
        for key, value in data.items():
            self.assertIn(key, form.errors)

    def test_pay_loan_form_account_and_loan_currencies_not_matching(self):
        loan_currency = CurrencyFactory()
        account_currency = CurrencyFactory()
        valid_loan = LoanFactory(user=self.user, currency=loan_currency)
        valid_account = AccountFactory(user=self.user, currency=account_currency)
        data = {
            "account": valid_account.id,
            "loan": valid_loan.id,
            "amount": 10,
            "date": datetime.date(2022, 2, 2),
        }
        form = PayLoanForm(user=self.user, data=data)
        self.assertIn(
            "Account and loan currencies can not be different.", form.errors["__all__"]
        )

    def test_pay_loan_form_with_invalid_account(self):
        currency = CurrencyFactory()
        valid_loan = LoanFactory(user=self.user, currency=currency)
        invalid_account = AccountFactory(currency=currency)
        data = {
            "account": invalid_account.id,
            "loan": valid_loan.id,
            "amount": 10,
            "date": datetime.date(2022, 2, 2),
        }
        form = PayLoanForm(user=self.user, data=data)
        self.assertIn("Invalid account or loan data.", form.errors["__all__"])

    def test_pay_loan_form_with_invalid_account(self):
        currency = CurrencyFactory()
        invalid_loan = LoanFactory(currency=currency)
        valid_account = AccountFactory(user=self.user, currency=currency)
        data = {
            "account": valid_account.id,
            "loan": invalid_loan.id,
            "amount": 10,
            "date": datetime.date(2022, 2, 2),
        }
        form = PayLoanForm(user=self.user, data=data)
        self.assertIn("Invalid account or loan data.", form.errors["__all__"])

    def test_loan_detail_pay_form_with_valid_data(self):
        currency = CurrencyFactory()
        valid_loan = LoanFactory(user=self.user, currency=currency)
        valid_account = AccountFactory(user=self.user, currency=currency)
        data = {
            "account": valid_account.id,
            "amount": 10,
            "date": datetime.date(2022, 2, 2),
        }
        form = LoanDetailPaymentForm(user=self.user, loan=valid_loan, data=data)
        for key, value in data.items():
            self.assertEquals(form[key].value(), value)

    def test_loan_detail_pay_form_with_invalid_data(self):
        currency = CurrencyFactory()
        invalid_loan = LoanFactory(currency=currency)
        invalid_account = AccountFactory(currency=currency)
        data = {
            "account": invalid_account.id,
            "amount": "invalid amount",
            "date": "invalid date",
        }
        form = LoanDetailPaymentForm(user=self.user, loan=invalid_loan, data=data)
        for key, value in data.items():
            self.assertIn(key, form.errors)

    def test_setup_form_with_valid_data(self):
        currency = CurrencyFactory()
        data = {
            'currency': currency.id
        }
        form = SetupForm(data=data)
        for key, value in data.items():
            self.assertEquals(form[key].value(), value)

    def test_edit_expense_transaction_form(self):
        user_account_1 = AccountFactory(user=self.user)
        user_account_2 = AccountFactory(user=self.user)
        expense_transaction = AccountTransactionFactory(content_object=user_account_1, type='E')
        data = {
            'name': 'test_name',
            'object_id': user_account_2.id,
            'amount': 1,
            'date': datetime.date(2022, 2, 2),
            'category': self.valid_expense_category.id,
        }
        form = EditTransactionForm(data=data, user=self.user, instance=expense_transaction)
        for key, value in data.items():
            self.assertEquals(form[key].value(), value)
    
    def test_create_credit_card_form(self):
        currency = CurrencyFactory()
        data = {
            'name': 'test_name',
            "balance": 5,
            "currency": currency.id,
            "payment_day": 5,
        }
        form = CreateCreditCardForm(data=data)
        for key, value in data.items():
            self.assertEquals(form[key].value(), value)
    
    def test_edit_income_transaction_form(self):
        user_account_1 = AccountFactory(user=self.user)
        user_account_2 = AccountFactory(user=self.user)
        income_transaction = AccountTransactionFactory(content_object=user_account_1, type='I')
        data = {
            'name': 'test_name',
            'object_id': user_account_2.id,
            'amount': 1,
            'date': datetime.date(2022, 2, 2),
            'category': self.valid_income_category.id,
        }
        form = EditTransactionForm(data=data, user=self.user, instance=income_transaction)
        for key, value in data.items():
            self.assertEquals(form[key].value(), value)