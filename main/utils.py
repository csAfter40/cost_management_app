from decimal import Decimal
from unicodedata import category
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce, ExtractMonth, ExtractYear
from django.db.models.signals import post_save
from django.core.paginator import Paginator
from .models import (
    User,
    UserPreferences,
    Account,
    Transfer,
    Category,
    Transaction,
    Loan,
    Rate,
)
from .categories import categories
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta


def get_latest_transactions(user, qty):
    account_ids = Account.objects.filter(user=user).values_list("id", flat=True)
    transactions = (
        Transaction.objects.filter(
            content_type__model="account", object_id__in=account_ids
        )
        .exclude(category__is_transfer=True)
        .order_by("-date")[:qty]
    )
    return transactions


def get_latest_transfers(user, qty):
    transfers = (
        Transfer.objects.filter(user=user)
        .prefetch_related(
            "from_transaction__content_object__currency",
            "to_transaction__content_object__currency",
        )
        .order_by("-date")[:qty]
    )
    return transfers


def create_categories(categories, user, parent=None):
    for key, value in categories.items():
        category = Category.objects.create(
            name=key,
            user=user,
            type=value["type"],
            is_transfer=value.get("is_transfer", False),
            is_protected=value.get("is_protected", False),
        )
        if parent:
            category.parent = parent
        category.save()
        if value["children"]:
            create_categories(categories=value["children"], user=user, parent=category)


def get_account_data(user):
    """
    Returns all accounts of a user and currencies of those accounts.
    """
    accounts = Account.objects.filter(user=user, is_active=True).select_related(
        "currency"
    )
    data = {}
    for account in accounts:
        data[account.id] = account.currency.code
    return data


def get_loan_data(user):
    """
    Returns all accounts of a user and currencies of those accounts.
    """
    loans = Loan.objects.filter(user=user, is_active=True).select_related("currency")
    data = {}
    for loan in loans:
        data[loan.id] = loan.currency.code
    return data


def validate_main_category_uniqueness(name, user, type):
    return not Category.objects.filter(
        name=name, user=user, parent=None, type=type
    ).exists()


def get_dates():
    dates = {}
    today = date.today()
    weekday = today.weekday()
    month = today.month
    year = today.year
    dates["today"] = today
    dates["week_start"] = today - timedelta(days=(weekday - 1))
    dates["month_start"] = date(year, month, 1)
    dates["year_start"] = date(year, 1, 1)
    return dates


def get_stats(qs, balance):
    expences = qs.filter(type="E").aggregate(Sum("amount"))
    incomes = qs.filter(type="I").aggregate(Sum("amount"))
    incomes_sum = incomes["amount__sum"] if incomes["amount__sum"] else 0
    expences_sum = expences["amount__sum"] if expences["amount__sum"] else 0
    diff = incomes_sum - expences_sum
    try:
        rate = f"{(diff / (balance-diff)):.2%}"
    except:
        rate = ""
    stats = {
        "rate": rate,
        "diff": diff,
    }
    return stats


def is_owner(user, model, id):
    object = get_object_or_404(model.objects.select_related("user"), id=id)
    return object.user == user


def get_category_stats(qs, category_type, parent, user):
    categories = Category.objects.filter(user=user, parent=parent, type=category_type)
    category_stats = {}
    for category in categories:
        descendant_categories = category.get_descendants(include_self=True)
        sum = qs.filter(category__in=descendant_categories).aggregate(Sum("amount"))
        if not sum["amount__sum"]:
            continue
        category_stats[category.name] = {"sum": sum["amount__sum"], "id": category.id}
    if not category_stats:
        category_stats["No data available"] = {"sum": 0, "id": 0}
    return category_stats


def get_subcategory_stats(qs, category):
    sum_data = []
    labels = []
    categories = category.get_descendants(include_self=True)
    for category in categories:
        sum = qs.filter(category=category).aggregate(Sum("amount"))
        if sum["amount__sum"]:
            labels.append(category.name)
            sum_data.append(sum["amount__sum"])
    data = {
        "data": sum_data,
        "labels": labels,
    }
    return data


def get_comparison_stats(expense_stats, income_stats):
    comparison_stats = {"Expense": 0, "Income": 0}
    for key, value in expense_stats.items():
        comparison_stats["Expense"] += value["sum"]
    for key, value in income_stats.items():
        comparison_stats["Income"] += value["sum"]
    return comparison_stats


def get_paginated_qs(qs, request, item_qty):
    paginator = Paginator(qs, item_qty)
    page_num = request.GET.get("page", 1)
    return paginator.get_page(page_num)


def get_loan_progress(loan_object):
    """
    Given a loan object, returns percentage of .
    """
    if loan_object.initial == 0:
        return "0.00"
    else:
        progress = (
            (loan_object.initial - loan_object.balance) / loan_object.initial
        ) * 100
        return round(progress, 2)


def get_payment_stats(loan_object):
    data = {}
    data[loan_object.created.strftime("%Y-%m-%d")] = abs(loan_object.initial)
    transactions = Transaction.objects.filter(
        content_type__model="loan", object_id=loan_object.id
    ).order_by("date")
    balance = loan_object.initial
    for tr in transactions:
        balance += tr.amount
        data[tr.date.strftime("%Y-%m-%d")] = abs(balance)
    return data


def get_monthly_asset_balance_change(asset):
    """
    Takes an asset(account or loan) and returns a queryset of dictionaries of monthly change.
    (total incomes - total expences)
    """
    transactions = Transaction.objects.filter(
        content_type__model=asset.__class__.__name__.lower(),
        object_id=asset.id,
    )
    monthly_total = (
        transactions.annotate(month=ExtractMonth("date"), year=ExtractYear("date"))
        .values("month", "year")
        .annotate(
            total=Coalesce(Sum("amount", filter=Q(type="I")), Decimal(0))
            - Coalesce(Sum("amount", filter=Q(type="E")), Decimal(0))
        )
        .order_by("year", "month")
    )
    return monthly_total


def sort_balance_data(data):
    """
    Takes a dictionary and returns a list of tuples sorted by dictionary keys.
    """
    return sorted(data.items())


def convert_str_to_date(str):
    return datetime.strptime(str, "%Y-%m")


def convert_date_to_str(date):
    return date.strftime("%Y-%m")


def get_next_month(date: str) -> str:
    datetime_obj = convert_str_to_date(date)
    new_date = datetime_obj + relativedelta(months=+1)
    return convert_date_to_str(new_date)


def fill_missing_monthly_data(data):
    start_date = min(data)
    end_date = max(data)
    current_date = start_date
    current_value = data[current_date]
    while current_date < end_date:
        if current_date in data:
            current_value = data[current_date]
        else:
            data[current_date] = current_value
        current_date = get_next_month(current_date)
    return data


def get_monthly_asset_balance(asset):
    """
    Takes an asset(account or loan) and returns a dictionary of monthly balance.
    (total incomes - total expences)
    """
    data = {}
    data[asset.created.strftime("%Y-%m")] = asset.initial
    monthly_totals = get_monthly_asset_balance_change(asset)
    balance = asset.initial
    for item in monthly_totals:
        balance += item["total"]
        data[f"{item['year']}-{item['month']:02d}"] = balance
    return data


def get_monthly_currency_balance(user, currency):
    """
    Takes an currency and returns a dictionary of monthly balance for all accounts in that currency.
    (total incomes - total expences)
    """
    accounts = Account.objects.filter(user=user, currency=currency)
    data = {}
    for account in accounts:
        monthly_balance = get_monthly_asset_balance(account)
        for key, value in monthly_balance.items():
            data[key] = data.get(key, 0) + value
    data = fill_missing_monthly_data(data)
    return sort_balance_data(data)


def get_user_currencies(user):
    """
    Takes a user and returns a set of user's active accounts.
    """
    currencies = set()
    active_user_accounts = Account.objects.filter(user=user, is_active=True)
    for account in active_user_accounts:
        currencies.add(account.currency)
    return currencies


def get_worth_stats(user):
    stats = {}
    currencies = get_user_currencies(user)
    for currency in currencies:
        stats[currency] = get_monthly_currency_balance(user=user, currency=currency)
    return stats


def convert_money(from_currency, to_currency, amount):
    """
    A basic currency converter. Takes from currency, to currency and an amount.
    Returns converted amount.
    """
    from_currency_rate = Rate.objects.get(currency=from_currency)
    to_currency_rate = Rate.objects.get(currency=to_currency)
    conversion_rate = to_currency_rate.rate / from_currency_rate.rate
    return amount * conversion_rate


def get_net_worth_by_currency(user, currency):
    """
    Takes user and currency objects and returns a decimal showing new worth of user in the currency.
    """
    accounts = Account.objects.filter(user=user, currency=currency, is_active=True)
    net_worth = 0
    for account in accounts:
        net_worth += account.balance
    return net_worth

def get_accounts_total_balance(account_data):
    '''
    Takes a dictionary of accounts data in which keys are accounts and values are 
    balances. Returns a decimal value of sum of all balances in the dictionary.
    '''
    total = 0
    for key, value in account_data.items():
        total += value
    return total

def get_currency_account_balances(user, currency):
    '''
    Takes a user and currency object and returns a dictionary of all account 
    balances of the user in the given currency.
    '''
    data = {}
    accounts = Account.objects.filter(user=user, currency=currency, is_active=True)
    for account in accounts:
        data[account] = account.balance
    return data

def get_user_net_worths(user):
    """
    Takes a user object and returns a dictionary of net worths in which keys are 
    currencies and values are total balance of all accounts of the user in that 
    currency.
    """
    net_worths = {}
    currencies = get_user_currencies(user)
    for currency in currencies:
        net_worth = get_net_worth_by_currency(user, currency)
        net_worths[currency] = net_worth
    return net_worths

def get_currency_details(user):
    """
    Takes a user and returns a dictionary of data in which keys are currencies(of the 
    user) and values are dictionaries that contains account(in that currency) balances 
    and total balance of the currency.
    """
    currency_details = {}
    currencies = get_user_currencies(user)
    for currency in currencies:
        details = get_currency_account_balances(user, currency)
        details['total'] = get_accounts_total_balance(details)
        currency_details[currency] = details
    return currency_details

def get_users_grand_total(user, data):
    """
    Takes a dictionary generated by get_currency_details function and returns 
    a dictionary of user's primary_currency and total money amount converted 
    to user's primary currency.
    """
    user_currency = user.user_preferences.primary_currency
    grand_total = 0
    for currency, totals in data.items():
        currency_total = totals['total']
        converted_total = convert_money(
            from_currency=currency, 
            to_currency=user_currency, 
            amount=currency_total
        )
        grand_total += converted_total
    return {'currency': user_currency, 'total': round(grand_total, 2)}

def withdraw_asset_balance(transaction):
    account = transaction.content_object
    amount = transaction.amount
    if transaction.type == 'E':
        account.balance += amount
    else:
        account.balance -= amount
    account.save()

def handle_transaction_delete(transaction_obj):
    with transaction.atomic():
        if transaction_obj.has_transfer():
            couple_transaction_obj = transaction_obj.get_couple_transaction()
            withdraw_asset_balance(transaction_obj)
            withdraw_asset_balance(couple_transaction_obj)
            couple_transaction_obj.delete()
        else: 
            withdraw_asset_balance(transaction_obj)
        transaction_obj.delete()

def edit_asset_balance(transaction):
    '''
    Edits account or loan balance when a transaction is made. Accepts a transaction object.
    '''
    asset = transaction.content_object
    amount = transaction.amount
    if transaction.type == 'E':
        asset.balance -= amount 
    else:
        asset.balance += amount 
    asset.save()

def create_transaction(data):
    '''
    Accepts a dictionary object, creates a transaction, edits related asset balance 
    and returns the created transaction object.
    '''
    with transaction.atomic():
        transaction_obj = Transaction.objects.create(**data)   
        edit_asset_balance(transaction_obj)
    return transaction_obj

def get_from_transaction(data, user):
    '''
    Accepts a data dictionary and user object. Extracts data for "from transaction" and creates from transaction object.
    Returns the created transaction object.
    '''
    from_data = {
        'content_object': data['from_account'],
        'name': 'Transfer Out',
        'amount': data['from_amount'],
        'date': data['date'],
        'category': Category.objects.filter(user=user, name="Transfer Out").first(),
        'type': 'E'
    }
    return create_transaction(from_data)

def get_to_transaction(data, user):
    '''
    Accepts a data dictionary and user object. Extracts data for "to transaction" and creates from transaction object.
    Returns the created transaction object.
    '''
    to_data = {
        'content_object': data['to_account'],
        'name': 'Transfer In',
        'amount': data['to_amount'],
        'date': data['date'],
        'category': Category.objects.filter(user=user, name="Transfer In").first(),
        'type': 'I'
    }
    return create_transaction(to_data)

def create_transfer(data, user):
    '''
    Accepts a data dictionary and user object. Creates a transfer object and related transaction objects.
    '''
    with transaction.atomic():
        from_transaction = get_from_transaction(data, user)
        to_transaction = get_to_transaction(data, user)
        Transfer.objects.create(
            user = user,
            from_transaction = from_transaction,
            to_transaction = to_transaction,
            date = data['date']
        )

def get_loan_payment_transaction_data(form, asset):
    '''
    Accepts a Django form and asset string. Creates and returns a data dictionary 
    required for creating a transaction object.
    '''
    data = form.cleaned_data
    category = Category.objects.get(user=form.user, name='Pay Loan')
    transaction_data = {
        'content_object': data.get(asset),
        'name': 'Pay Loan',
        'amount': abs(data.get('amount')),
        'date': data.get('date'),
        'category': category,
        'type': 'E' if asset == 'account' else 'I'
    }
    return transaction_data

def handle_loan_payment(form):
    '''
    Accepts a Django form, creates transaction and transfer objects needed for loan payment process.
    '''
    with transaction.atomic():
        account_transaction = create_transaction(get_loan_payment_transaction_data(form, asset='account'))
        loan_transaction = create_transaction(get_loan_payment_transaction_data(form, asset='loan'))
        Transfer.objects.create(
                user = form.user,
                from_transaction = account_transaction,
                to_transaction = loan_transaction,
                date = account_transaction.date
            )

@receiver(post_save, sender=User)
def create_user_categories(sender, instance, created, **kwargs):
    if created:
        create_categories(categories, instance)


@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    if created:
        UserPreferences.objects.create(user=instance)
