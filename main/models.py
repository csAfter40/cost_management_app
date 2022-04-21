from django.db import models
from django.contrib.auth.models import AbstractUser
from mptt.models import MPTTModel, TreeForeignKey
from datetime import date
from wallet.settings import DEFAULT_CURRENCY_PK


class User(AbstractUser):
    
    def __str__(self) -> str:
        return self.username

class Currency(models.Model):
    code = models.CharField(max_length=2)
    name = models.CharField(max_length=32)
    symbol = models.CharField(max_length=8, null=True, blank=True)

    def __str__(self):
        return self.code


class UserPreferences(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, default=DEFAULT_CURRENCY_PK)

    def __str__(self):
        return f"{self.user} preferences"


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, default=DEFAULT_CURRENCY_PK)

    def __str__(self):
        return self.name


class ExpenseCategory(MPTTModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=64)
    slug = models.SlugField()
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        unique_together = (('parent', 'slug'))
        verbose_name_plural = 'ExpenseCategories'

    def __str__(self) -> str:
        return self.slug

class IncomeCategory(MPTTModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=64)
    slug = models.SlugField()
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        unique_together = (('parent', 'slug'))
        verbose_name_plural = 'IncomeCategories'

    def __str__(self) -> str:
        return self.slug

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField(blank=True, default=date.today)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name} - {self.amount} from {self.account}"


class Expense(Transaction):
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True)

    def get_type(self):
        return "Expense"


class Income(Transaction):
    category = models.ForeignKey(IncomeCategory, on_delete=models.SET_NULL, null=True)

    def get_type(self):
        return "Income"

class Transfer(models.Model):
    from_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='outgoings')
    to_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='incomings' )
    from_amount = models.DecimalField(max_digits=14, decimal_places=2)
    to_amount = models.DecimalField(max_digits=14, decimal_places=2, blank=True)
    date = models.DateField(blank=True, default=date.today)

    def __str__(self):
        return f"On {self.date} from {self.from_account} to {self.to_account} {self.from_amount}"