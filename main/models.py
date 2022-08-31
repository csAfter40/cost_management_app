from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from mptt.models import MPTTModel, TreeForeignKey
from datetime import date
from wallet.settings import DEFAULT_CURRENCY_PK


class User(AbstractUser):
    def __str__(self) -> str:
        return self.username


class Currency(models.Model):
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=128)
    symbol = models.CharField(max_length=8, null=True, blank=True)

    def __str__(self):
        return self.code


class UserPreferences(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.ForeignKey(
        Currency, on_delete=models.SET_DEFAULT, default=DEFAULT_CURRENCY_PK
    )

    def __str__(self):
        return f"{self.user} preferences"


class Assets(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.ForeignKey(
        Currency, on_delete=models.SET_DEFAULT, default=DEFAULT_CURRENCY_PK
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        unique_together = ('user', 'name')


class Account(Assets):
    pass


class Loan(Assets):
    initial = models.DecimalField(max_digits=14, decimal_places=2, default=0)


class Category(MPTTModel):

    CATEGORY_TYPES = (
        ("E", "Expense"),
        ("I", "Income"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=64)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    type = models.CharField(max_length=1, choices=CATEGORY_TYPES)
    is_transfer = models.BooleanField(default=False)
    is_protected = models.BooleanField(default=False)

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        unique_together = ("parent", "name")
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


class Transaction(models.Model):

    TRANSACTION_TYPES = (
        ("E", "Expense"),
        ("I", "Income"),
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, default=ContentType.objects.get(app_label='main', model='account').id)
    object_id = models.PositiveIntegerField(default=7)
    content_object = GenericForeignKey('content_type', 'object_id')

    name = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField(blank=True, default=date.today)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=2, choices=TRANSACTION_TYPES)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.amount} from {self.account}"


class Transfer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Transfers")
    from_transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="transfers_from", null=True
    )
    to_transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="transfers_to", null=True
    )
    date = models.DateField(blank=True, default=date.today)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"On {self.date} from {self.from_transaction.account} to {self.to_transaction.account} {self.from_transaction.amount}"
