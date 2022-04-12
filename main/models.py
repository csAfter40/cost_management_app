from django.db import models
from django.contrib.auth.models import AbstractUser
from mptt.models import MPTTModel, TreeForeignKey


class User(AbstractUser):
    
    def __str__(self) -> str:
        return self.username


class Currency(models.Model):
    code = models.CharField(max_length=2)
    name = models.CharField(max_length=32)
    symbol = models.CharField(max_length=8, null=True, blank=True)

    def __str__(self):
        return self.code


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    balance = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)


class CostCategory(MPTTModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=64)
    slug = models.SlugField()
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        unique_together = (('parent', 'slug'))
        verbose_name_plural = 'CostCategories'

    def __str__(self) -> str:
        return f"{self.user} - {self.slug}"

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
        return f"{self.user} - {self.slug}"


class Cost(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, )


class Income(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, )


class Transfer(models.Model):
    from_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='outgoings')
    to_accout = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='incomings' )
    amount = models.DecimalField(max_digits=14, decimal_places=2)