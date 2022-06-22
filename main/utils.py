from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import User, ExpenseCategory, IncomeCategory, UserPreferences, Expense, Income, Account, Transfer
from .categories import expense_categories, income_categories

def get_latest_transactions(user, qty):
    accounts = Account.objects.filter(user=user)
    expenses = Expense.objects.filter(account__in=accounts).order_by('-date')
    incomes = Income.objects.filter(account__in=accounts).order_by('-date')
    expenses_len = expenses.count()
    incomes_len = incomes.count()
    transaction_list = []
    j, k = 0, 0
    for i in range(qty):
        if j < expenses_len and k < incomes_len:
            if expenses[j].date >= incomes[k].date:
                transaction_list.append(expenses[j])
                j += 1
            else:
                transaction_list.append(incomes[k])
                k += 1
        elif j < expenses_len:
            transaction_list.append(expenses[j])
            j += 1
        elif k < incomes_len:
            transaction_list.append(incomes[k])
            k += 1
        else:
            break
    return transaction_list

def get_latest_transfers(user, qty):
    accounts = Account.objects.filter(user=user)
    transfers = Transfer.objects.filter(from_account__in=accounts).order_by('-date')[:qty]
    return transfers

def create_categories(model, categories, user, parent=None):
    for key, value in categories.items():
        category = model.objects.create(name=key, user=user)
        if parent:
            category.parent = parent
        category.save()
        if value['children']:
            create_categories(
                model,
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

def validate_main_category_uniqueness(name, user, category):
    return not category.objects.filter(name=name, user=user, parent=None).exists()

@receiver(post_save, sender=User)
def create_user_categories(sender, instance, created, **kwargs):
    if created:
        create_categories(ExpenseCategory, expense_categories, instance)
        create_categories(IncomeCategory, income_categories, instance)

@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    if created:
        UserPreferences.objects.create(user=instance)