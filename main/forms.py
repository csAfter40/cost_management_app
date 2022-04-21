from django.forms import CharField, ModelForm, TextInput, Select, ValidationError
from .models import Expense, Income, ExpenseCategory, IncomeCategory, Account, Transfer
from mptt.forms import TreeNodeChoiceField

class ExpenseInputForm(ModelForm):

    category = TreeNodeChoiceField(None)
    name = CharField(max_length=128, label="Description")
    
    class Meta:
        model = Expense
        fields = ['name', 'account', 'amount', 'category', 'date']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control autocomplete-input'}),
            'date': TextInput(attrs={'id': 'expense-datepicker'}),
        }
        
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ExpenseCategory.objects.filter(user=self.user)
        self.fields['account'].queryset = Account.objects.filter(user=self.user)
        

class IncomeInputForm(ModelForm):

    category = TreeNodeChoiceField(None)
    name = CharField(max_length=128, label="Description")

    class Meta:
        model = Income
        fields = ['name', 'account', 'amount', 'category', 'date']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control autocomplete-input'}),
            'date': TextInput(attrs={'id': 'income-datepicker'}),
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = IncomeCategory.objects.filter(user=self.user)
        self.fields['account'].queryset = Account.objects.filter(user=self.user)


class TransferForm(ModelForm):

    class Meta:
        model = Transfer
        fields = ['from_account', 'to_account', 'from_amount', 'to_amount', 'date']
        widgets = {
            'date': TextInput(attrs={'id': 'transfer-datepicker'}),
            'from_account': Select(attrs={'id': 'from-account-field'}),
            'to_account': Select(attrs={'id': 'to-account-field'}),
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        accounts_qs = Account.objects.filter(user=self.user)
        self.fields['from_account'].queryset = accounts_qs
        self.fields['to_account'].queryset = accounts_qs

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['from_account'] == cleaned_data['to_account']:
            raise ValidationError("From account and To account can not have same value")
        return cleaned_data # ???
