from django import forms
from django.forms import CharField, ModelForm, TextInput, Select, ValidationError
from .models import Account, Transaction, Transfer, Category
from mptt.forms import TreeNodeChoiceField
from datetime import date

class ExpenseInputForm(ModelForm):

    category = TreeNodeChoiceField(None)
    name = CharField(max_length=128, label="Description")
    
    class Meta:
        model = Transaction
        fields = ['name', 'account', 'amount', 'category', 'date']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control autocomplete-input'}),
            'date': TextInput(attrs={'id': 'expense-datepicker'}),
        }
        
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=self.user, type='E')
        self.fields['account'].queryset = Account.objects.filter(user=self.user)
        

class IncomeInputForm(ModelForm):

    category = TreeNodeChoiceField(None)
    name = CharField(max_length=128, label="Description")

    class Meta:
        model = Transaction
        fields = ['name', 'account', 'amount', 'category', 'date']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control autocomplete-input'}),
            'date': TextInput(attrs={'id': 'income-datepicker'}),
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=self.user, type='I')
        self.fields['account'].queryset = Account.objects.filter(user=self.user)


# class TransferForm(ModelForm):


#     class Meta:
#         model = Transfer
#         fields = ['date']
#         widgets = {
#             'date': TextInput(attrs={'id': 'transfer-datepicker'}),
#             'from_account': Select(attrs={'id': 'from-account-field'}),
#             'to_account': Select(attrs={'id': 'to-account-field'}),
#         }

#     def __init__(self, user, *args, **kwargs):
#         self.user = user
#         super().__init__(*args, **kwargs)
#         accounts_qs = Account.objects.filter(user=self.user)
#         self.fields['from_account'].queryset = accounts_qs
#         self.fields['to_account'].queryset = accounts_qs

#     def clean(self):
#         cleaned_data = super().clean()
#         if cleaned_data['from_account'] == cleaned_data['to_account']:
#             raise ValidationError("From account and To account can not have same value")
#         return cleaned_data # ???

class TransferForm(forms.Form):

    from_amount = forms.DecimalField(decimal_places=2)
    to_amount = forms.DecimalField(decimal_places=2)
    date = forms.DateField(initial=date.today, widget=TextInput(attrs={'id': 'transfer-datepicker'}))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            qs = Account.objects.filter(user=user)
            self.fields['from_account'] = forms.ModelChoiceField(queryset=qs, widget=Select(attrs={'id': 'from-account-field'}))
            self.fields['to_account'] = forms.ModelChoiceField(queryset=qs, widget=Select(attrs={'id': 'to-account-field'}))

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['from_account'] == cleaned_data['to_account']:
            raise ValidationError('From account and To account can not have same value.')
        return cleaned_data
    