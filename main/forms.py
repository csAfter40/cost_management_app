from django.forms import ModelForm
from .models import Account

class AccountForm(ModelForm):
    model = Account
    fields = ['name', 'balance', 'currency']