from django import forms
from django.forms import CharField, ModelForm, TextInput
from .models import Expense, Income, ExpenseCategory, IncomeCategory, Account
from mptt.forms import TreeNodeChoiceField

class ExpenseInputForm(ModelForm):

    category = TreeNodeChoiceField(None)
    name = CharField(max_length=128, label="Description")
    
    class Meta:
        model = Expense
        fields = ['name', 'account', 'amount', 'category']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control autocomplete-input'}),
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
        fields = ['name', 'account', 'amount', 'category']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control autocomplete-input'}),
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = IncomeCategory.objects.filter(user=self.user)
        self.fields['account'].queryset = Account.objects.filter(user=self.user)
