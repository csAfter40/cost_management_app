from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import User, UserPreferences, Account, Transfer, Category, Transaction
from .categories import categories
from datetime import date, timedelta
def get_latest_transactions(user, qty):
    accounts = Account.objects.filter(user = user)
    transactions = Transaction.objects.filter(account__in=accounts).exclude(type__startswith='T').order_by('-date')[:qty]
    return transactions

def get_latest_transfers(user, qty):
    transfers = Transfer.objects.filter(user=user).select_related('from_transaction__account__currency', 'to_transaction__account__currency').order_by('-date')[:qty]
    return transfers

def create_categories(categories, user, parent=None):
    for key, value in categories.items():
        category = Category.objects.create(name=key, user=user, type=value['type'])
        if parent:
            category.parent = parent
        category.save()
        if value['children']:
            create_categories(
                categories=value['children'],
                user=user,
                parent=category
            )

def get_account_data(user):
    """
        Returns all accounts of a user and currencies of those accounts.
    """
    accounts = Account.objects.filter(user=user).select_related('currency')
    data = {}
    for account in accounts:
        data[account.id] = account.currency.code
    return data

def validate_main_category_uniqueness(name, user, type):
    return not Category.objects.filter(name=name, user=user, parent=None, type=type).exists()

def get_dates():
    dates = {}
    today = date.today()
    weekday = today.weekday()
    month = today.month
    year = today.year
    dates['today'] = today
    dates['week_start'] = today - timedelta(days=(weekday-1))
    dates['month_start'] = date(year, month, 1)
    dates['year_start'] = date(year, 1, 1)
    return dates

@receiver(post_save, sender=User)
def create_user_categories(sender, instance, created, **kwargs):
    if created:
        create_categories(categories, instance)

@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    if created:
        UserPreferences.objects.create(user=instance)