from django.db import models
from django.db.models import UniqueConstraint, CheckConstraint, Q
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.sessions.models import Session
from mptt.models import MPTTModel, TreeForeignKey
from datetime import date
from dateutil.relativedelta import relativedelta
from wallet.settings import DEFAULT_CURRENCY_PK
from django.urls import reverse


class User(AbstractUser):
    is_guest = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.username

    @property
    def primary_currency(self):
        return self.user_preferences.primary_currency


class Currency(models.Model):
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=128)
    symbol = models.CharField(max_length=8, null=True, blank=True)

    def __str__(self):
        return self.code

    def get_rate(self):
        return self.rate.rate


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

    @property
    def class_name(self):
        return self.__class__.__name__

    def is_expense_category(self):
        return True if self.type=='E' else False


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
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='transactions')
    type = models.CharField(max_length=2, choices=TRANSACTION_TYPES)
    installments = models.PositiveIntegerField(blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(installments__gte=2) & Q(installments__lte=36), 
                name='installments_btw_0_36'
            )
        ]

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

    def save(self, *args, **kwargs):
        from .utils import get_transaction_installment_due_date
        self.amount = abs(self.amount)
        if isinstance(self.content_object, CreditCard):
            if self.installments:
                self.due_date = get_transaction_installment_due_date(self.date, self.installments, self.content_object)
            else:
                self.due_date = self.content_object.get_next_payment_date(self.date)
        super().save(*args, **kwargs)

    @property
    def installment_amount(self):
        if self.installments:
            return round(self.amount/self.installments, 2)
        return None

    @property
    def class_name(self):
        return self.__class__.__name__

    @property
    def delete_url(self):
        return reverse('main:delete_transaction', kwargs={'pk': self.id})

    @property
    def is_editable(self):
        return self.content_object.is_active

    @property
    def user(self):
        return self.content_object.user


class Assets(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    initial = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def class_name(self):
        return self.__class__.__name__

    class Meta:
        abstract = True
    

class Account(Assets):
    transactions = GenericRelation(Transaction, related_query_name='account')
    currency = models.ForeignKey(
        Currency, on_delete=models.SET_DEFAULT, default=DEFAULT_CURRENCY_PK, related_name='accounts'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['name', 'user'], 
                condition=Q(is_active=True), 
                name='unique account name and user when active'
            )
        ]
    
    @property
    def delete_url(self):
        return reverse('main:delete_account', kwargs={'pk':self.id})


class Loan(Assets):
    transactions = GenericRelation(Transaction, related_query_name='loan')
    currency = models.ForeignKey(
        Currency, on_delete=models.SET_DEFAULT, default=DEFAULT_CURRENCY_PK, related_name='loans'
    )
    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['name', 'user'], 
                condition=Q(is_active=True), 
                name='unique loan name and user when active'
            )
        ]
    
    @property
    def delete_url(self):
        return reverse('main:delete_loan', kwargs={'pk':self.id})


class CreditCard(Assets):
    transactions = GenericRelation(Transaction, related_query_name='credit_card')
    currency = models.ForeignKey(
        Currency, on_delete=models.SET_DEFAULT, default=DEFAULT_CURRENCY_PK, related_name='credit_cards'
    )
    payment_day = models.PositiveIntegerField() # day of the month
    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['name', 'user'], 
                condition=Q(is_active=True), 
                name='unique card name and user when active'
            ),
            CheckConstraint(
                check=Q(payment_day__gte=1) & Q(payment_day__lte=31), 
                name='payment_day_between_1-31'
            )
        ]

    def get_next_payment_date(self, current_date):
        from .utils import get_next_month, get_valid_date # import the function here due to circular import
        if current_date.day <= self.payment_day:
            return get_valid_date(current_date.year, current_date.month, self.payment_day)
        next_month = get_next_month(f"{current_date.year}-{current_date.month}").split("-")
        return get_valid_date(int(next_month[0]), int(next_month[1]), self.payment_day)
    
    def get_previous_payment_date(self, current_date):
        first_day_of_the_month = date(current_date.year, current_date.month, 1)
        first_day_of_the_previous_month = first_day_of_the_month + relativedelta(months=-1)
        return self.get_next_payment_date(first_day_of_the_previous_month)
    
    @property
    def next_payment_date(self):
        return self.get_next_payment_date(date.today())

    @property
    def delete_url(self):
        return reverse('main:delete_credit_card', kwargs={'pk':self.id})


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

    @property
    def class_name(self):
        return self.__class__.__name__

    @property
    def delete_url(self):
        return reverse('main:delete_transfer', kwargs={'pk': self.id})

    @property
    def is_editable(self):
        return self.from_transaction.is_editable and self.to_transaction.is_editable

class Rate(models.Model):
    currency = models.OneToOneField(Currency, on_delete=models.CASCADE, related_name='rate')
    rate = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.currency} - {self.rate}'
    

class GuestUserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="guest_user_session")
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="guest_user_session")