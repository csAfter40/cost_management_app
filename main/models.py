from django.db import models
from django.db.models import UniqueConstraint, Q
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_preferences')
    primary_currency = models.ForeignKey(
        Currency, on_delete=models.SET_DEFAULT, default=DEFAULT_CURRENCY_PK
    )

    def __str__(self):
        return f"{self.user} preferences"


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
        return f"{self.name} - {self.amount} on {self.content_object}"

    def has_transfer(self):
        '''
            Returns True if transaction belongs to a transfer.
        '''
        return self.transfer_to.exists() or self.transfer_from.exists()

    def get_couple_transaction(self):
        '''
            If the transaction belongs to a transfer, this method returns the other transaction in the transfer object.
        '''
        if self.has_transfer():
            if self.transfer_to.exists():
                return self.transfer_to.first().from_transaction
            else:
                return self.transfer_from.first().to_transaction
        return None


class Assets(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.ForeignKey(
        Currency, on_delete=models.SET_DEFAULT, default=DEFAULT_CURRENCY_PK
    )
    is_active = models.BooleanField(default=True)
    transactions = GenericRelation(Transaction)
    initial = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
    

class Account(Assets):
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['name', 'user'], 
                condition=Q(is_active=True), 
                name='unique account name and user when active'
            )
        ]


class Loan(Assets):
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['name', 'user'], 
                condition=Q(is_active=True), 
                name='unique loan name and user when active'
            )
        ]
    

class Transfer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Transfers")
    from_transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="transfer_from", null=True
    )
    to_transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="transfer_to", null=True
    )
    date = models.DateField(blank=True, default=date.today)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"On {self.date} from {self.from_transaction.content_object} to {self.to_transaction.content_object} {self.from_transaction.amount}"


class Rate(models.Model):
    currency = models.OneToOneField(Currency, on_delete=models.CASCADE, related_name='rate')
    rate = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.currency} - {self.rate}'