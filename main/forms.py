from django import forms
from django.forms import (
    CharField,
    HiddenInput,
    ModelForm,
    TextInput,
    Select,
    ValidationError,
    ModelChoiceField,
    IntegerField,
    RadioSelect
)

from .models import Account, Currency, Transaction, Transfer, Category, Loan, CreditCard
from mptt.forms import TreeNodeChoiceField
from datetime import date
from .form_fields import MathDecimalField

class MyModelChoiceField(ModelChoiceField):

   def to_python(self, value):
        try:
            value = super(MyModelChoiceField, self).to_python(value)
        except:
            key = self.to_field_name or 'pk'
            value = CreditCard.objects.filter(**{key: value})
            if not value.exists():
               raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
            else:
               value= value.first()
        return value

class ExpenseInputForm(ModelForm):
    ASSET_CHOICES = [
        ('account', 'Account'),
        ('card', 'Credit Card'),
    ]
    expense_asset = forms.ChoiceField(
        widget=RadioSelect(),
        choices=ASSET_CHOICES,
        initial='account',
        label=False
    )
    category = TreeNodeChoiceField(None)
    name = CharField(max_length=128, label="Description")
    content_object = MyModelChoiceField(queryset=None, label='Account')
    installments = forms.ChoiceField(
        choices=[("", "No Installments")]+[(str(x), f"{x} months") for x in range(2,37)],
        initial="",
        required=False
    )
    amount = MathDecimalField(
        max_digits=5, decimal_places=2, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Decimal or simple arithmetic.'})
    )

    class Meta:
        model = Transaction
        fields = ["name", "amount", "category", "date", "type"]
        widgets = {
            "name": TextInput(attrs={"class": "form-control autocomplete-input"}),
            "date": TextInput(attrs={"id": "expense-datepicker"}),
            "type": HiddenInput(attrs={"value": "E"}),
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.accounts = Account.objects.filter(user=self.user, is_active=True)
        self.cards = CreditCard.objects.filter(user=self.user, is_active=True)
        self.fields["category"].queryset = Category.objects.filter(
            user=self.user, type="E", is_protected=False
        )
        self.fields["content_object"].queryset = self.accounts

    def clean(self):
        cleaned_data = super().clean()
        try:
            cleaned_data["installments"] = cleaned_data["installments"] if cleaned_data["installments"] else None
        except KeyError:
            cleaned_data["installments"] = None
        if cleaned_data.get("expense_asset", None):
            del cleaned_data['expense_asset']
        form_date = cleaned_data.get('date', None)
        if form_date and form_date > date.today():
            raise ValidationError("Future transactions are not permitted.") 
        asset = cleaned_data.get("content_object", None)
        if asset not in self.accounts and not asset in self.cards:
            raise ValidationError("Account/Credit Card not found")
        if isinstance(asset, Account) and cleaned_data["installments"] is not None:
            raise ValidationError("Installment plan is only availavle for credit cards.")
        return cleaned_data

    def save(self, commit=True):
        transaction = super().save(commit=False)
        transaction.content_object = self.cleaned_data["content_object"]
        if commit:
            transaction.save()
        return transaction


class IncomeInputForm(ModelForm):

    ASSET_CHOICES = [
        ('account', 'Account'),
        ('card', 'Credit Card'),
    ]
    income_asset = forms.ChoiceField(
        widget=RadioSelect(),
        choices=ASSET_CHOICES,
        initial='account',
        label=False
    )
    category = TreeNodeChoiceField(None)
    name = CharField(max_length=128, label="Description")
    content_object = MyModelChoiceField(queryset=None, label='Account')
    amount = MathDecimalField(
        max_digits=14, decimal_places=2, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Decimal or simple arithmetic.'})
    )

    class Meta:
        model = Transaction
        fields = ["name", "amount", "category", "date", "type"]
        widgets = {
            "name": TextInput(attrs={"class": "form-control autocomplete-input"}),
            "date": TextInput(attrs={"id": "income-datepicker"}),
            "type": HiddenInput(attrs={"value": "I"}),
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.filter(
            user=self.user, type="I", is_protected=False
        )
        self.fields["content_object"].queryset = Account.objects.filter(
            user=self.user, is_active=True
        )
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("income_asset", None):
            del cleaned_data['income_asset']
        form_date = cleaned_data.get('date', None)
        if form_date and form_date > date.today():
            raise ValidationError("Future transactions are not permitted.")            
        return cleaned_data

    def save(self, commit=True):
        transaction = super().save(commit=False)
        transaction.content_object = self.cleaned_data["content_object"]
        if commit:
            transaction.save()
        return transaction


class TransferForm(forms.Form):

    from_amount = forms.DecimalField(decimal_places=2)
    to_amount = forms.DecimalField(decimal_places=2)
    date = forms.DateField(
        initial=date.today, widget=TextInput(attrs={"id": "transfer-datepicker"})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            qs = Account.objects.filter(user=user, is_active=True)
            self.fields["from_account"] = forms.ModelChoiceField(
                queryset=qs, widget=Select(attrs={"id": "from-account-field"})
            )
            self.fields["to_account"] = forms.ModelChoiceField(
                queryset=qs, widget=Select(attrs={"id": "to-account-field"})
            )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("from_account") and cleaned_data.get("to_account"):
            if cleaned_data["from_account"] == cleaned_data["to_account"]:
                raise ValidationError(
                    "From account and To account can not have same value."
                )
        form_date = cleaned_data.get('date', None)
        if form_date and form_date > date.today():
        # if cleaned_data['date'] > date.today():
            raise ValidationError("Future transfers are not permitted.")
        return cleaned_data


class PayLoanForm(forms.Form):

    amount = forms.DecimalField(decimal_places=2)
    date = forms.DateField(
        initial=date.today, widget=TextInput(attrs={"id": "loan-pay-datepicker"})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            qs_account = Account.objects.filter(user=user, is_active=True)
            qs_loan = Loan.objects.filter(user=user, is_active=True)
            self.fields["account"] = forms.ModelChoiceField(
                queryset=qs_account, widget=Select(attrs={"id": "account-field"})
            )
            self.fields["loan"] = forms.ModelChoiceField(
                queryset=qs_loan, widget=Select(attrs={"id": "loan-field"})
            )
            self.user = user
        self.fields["account"].label_from_instance = self.label_from_instance
        self.fields["loan"].label_from_instance = self.label_from_instance

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("account", None) and cleaned_data.get("loan", None):
            if cleaned_data["account"].currency != cleaned_data["loan"].currency:
                raise ValidationError(
                    "Account and loan currencies can not be different."
                )
        else:
            raise ValidationError("Invalid account or loan data.")
        return cleaned_data

    @staticmethod
    def label_from_instance(obj):
        """
        Method for overriding label_from_instance method of ModelChoiceField. 
        Edits text of choice field.
        """
        return f"{obj.name}  ({obj.balance} {obj.currency})"


class PayCreditCardForm(forms.Form):
    amount = forms.DecimalField(decimal_places=2)
    date = forms.DateField(
        initial=date.today, widget=TextInput(attrs={"id": "card-pay-datepicker"})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            qs_account = Account.objects.filter(user=user, is_active=True)
            qs_card = CreditCard.objects.filter(user=user, is_active=True)
            self.fields["account"] = forms.ModelChoiceField(
                queryset=qs_account, widget=Select(attrs={"id": "account-field"})
            )
            self.fields["card"] = forms.ModelChoiceField(
                queryset=qs_card, widget=Select(attrs={"id": "card-field"})
            )
            self.user = user
        self.fields["account"].label_from_instance = self.label_from_instance
        self.fields["card"].label_from_instance = self.label_from_instance

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("account", None) and cleaned_data.get("card", None):
            if cleaned_data["account"].currency != cleaned_data["card"].currency:
                raise ValidationError(
                    "Account and credit card currencies can not be different."
                )
        else:
            raise ValidationError("Invalid account or credit card data.")
        return cleaned_data

    @staticmethod
    def label_from_instance(obj):
        """
        Method for overriding label_from_instance method of ModelChoiceField. 
        Edits text of choice field.
        """
        return f"{obj.name}  ({obj.balance} {obj.currency})"


class LoanDetailPaymentForm(forms.Form):

    amount = forms.DecimalField(decimal_places=2)
    date = forms.DateField(
        initial=date.today, widget=TextInput(attrs={"id": "loan-pay-datepicker"})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        loan = kwargs.pop("loan", None)
        currency = loan.currency
        super().__init__(*args, **kwargs)
        if user and loan:
            qs_account = Account.objects.filter(
                user=user, is_active=True, currency=currency
            )
            self.fields["account"] = forms.ModelChoiceField(
                queryset=qs_account, widget=Select(attrs={"id": "account-field"})
            )


class SetupForm(forms.Form):
    currency = forms.ModelChoiceField(
        queryset=Currency.objects.all(),
        widget=Select(attrs={"class": "my-2"}),
        label="Primary Currency",
    )


class EditTransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ['name', 'amount', 'category', 'date', 'object_id']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        self.fields['object_id'] = forms.ModelChoiceField(
            queryset=Account.objects.filter(user=user, is_active=True),
            label='Account'
        )
        self.fields['category'] = TreeNodeChoiceField(
            queryset=Category.objects.filter(user=user, is_transfer=False, is_protected=False, type=instance.type)
        )

    def clean(self):
        data = self.cleaned_data
        data['object_id'] = data["object_id"].id
        return data


class CreateCreditCardForm(ModelForm):
    class Meta:
        model = CreditCard
        fields = ["name", "balance", "currency", "payment_day"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["payment_day"] = IntegerField(max_value=31, min_value=1, required=True)