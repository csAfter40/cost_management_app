from django import forms
from django.forms import (
    CharField,
    HiddenInput,
    ModelForm,
    TextInput,
    Select,
    ValidationError,
    ModelChoiceField,
)
from .models import Account, Transaction, Transfer, Category, Loan
from mptt.forms import TreeNodeChoiceField
from datetime import date


class ExpenseInputForm(ModelForm):

    category = TreeNodeChoiceField(None)
    name = CharField(max_length=128, label="Description")
    account = ModelChoiceField(
        queryset=None
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
        self.fields["category"].queryset = Category.objects.filter(
            user=self.user, type="E", is_protected=False
        )
        self.fields["account"].queryset = Account.objects.filter(
            user=self.user, is_active=True
        )

    def save(self, commit=True):
        transaction = super().save(commit=False)
        transaction.content_object = self.cleaned_data['account']
        if commit:
            transaction.save()
        return transaction


class IncomeInputForm(ModelForm):

    category = TreeNodeChoiceField(None)
    name = CharField(max_length=128, label="Description")
    account = ModelChoiceField(queryset=None)

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
        self.fields["account"].queryset = Account.objects.filter(
            user=self.user, is_active=True
        )
        
    def save(self, commit=True):
        transaction = super().save(commit=False)
        transaction.content_object = self.cleaned_data['account']
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
        if cleaned_data.get('from_account') and cleaned_data.get('to_account'):
            if cleaned_data["from_account"] == cleaned_data["to_account"]:
                raise ValidationError(
                    "From account and To account can not have same value."
                )
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

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('account', None) and cleaned_data.get('loan', None):
            if cleaned_data["account"].currency != cleaned_data["loan"].currency:
                raise ValidationError(
                    "Account and loan currencies can not be different."
                )
        else:
            raise ValidationError(
                    "Invalid account or loan data."
                )
        return cleaned_data
