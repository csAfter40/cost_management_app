from decimal import Decimal
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q, Sum, F
from django.db.models.functions import Coalesce, ExtractMonth, ExtractYear
from django.db.models.signals import post_save
from django.core.paginator import Paginator
from django.contrib.sessions.models import Session
from .models import (
    Currency,
    User,
    UserPreferences,
    Account,
    Transfer,
    Category,
    Transaction,
    Loan,
    Rate,
    CreditCard,
    GuestUserSession,
)
from .categories import categories
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
import uuid
import random
import string
from django.contrib.auth import login


def get_latest_transactions(user, qty):
    account_ids = Account.objects.filter(user=user).values_list("id", flat=True)
    card_ids = CreditCard.objects.filter(user=user).values_list("id", flat=True)
    transactions = (
        Transaction.objects.filter(
            # content_type__model="account", object_id__in=account_ids
            Q(content_type__model="account") & Q(object_id__in=account_ids) | 
            Q(content_type__model="creditcard") & Q(object_id__in=card_ids)
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
        .exclude(from_transaction__name="Pay Debt")
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
            parent.refresh_from_db()
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

def get_account_balance_data(user):
    """
    Returns all accounts of a user and balances accounts.
    """
    accounts = Account.objects.filter(user=user, is_active=True)
    data = {}
    for account in accounts:
        data[account.id] = account.balance
    return data


def get_loan_data(user):
    """
    Returns all loans of a user and currencies of those loans.
    """
    loans = Loan.objects.filter(user=user, is_active=True).select_related("currency")
    data = {}
    for loan in loans:
        data[loan.id] = loan.currency.code
    return data

def get_credit_card_data(user):
    """
    Returns all credit cards of a user and currencies of those loans.
    """
    cards = CreditCard.objects.filter(user=user, is_active=True).select_related("currency")
    data = {}
    for card in cards:
        data[card.id] = card.currency.code
    return data

def get_loan_balance_data(user):
    """
    Returns all loans of a user and balances of those loans.
    """
    loans = Loan.objects.filter(user=user, is_active=True)
    data = {}
    for loan in loans:
        data[loan.id] = loan.balance
    return data

def get_credit_card_balance_data(user):
    """
    Returns all credit cards of a user and balances of those cards.
    """
    cards = CreditCard.objects.filter(user=user, is_active=True)
    data = {}
    for card in cards:
        data[card.id] = card.balance
    return data

def add_installments_to_payment_plan(expense, payment_plan, card):
    """
    Given a transaction, a payment plan and a card, add all installment payments to payment plan.
    """
    current_date = expense.due_date.date()
    if expense.installments:
        while current_date >= card.next_payment_date:
            payment_plan[current_date] = payment_plan.get(current_date, 0) + expense.installment_amount
            current_date = card.get_previous_payment_date(current_date)
    else:
        payment_plan[current_date] = payment_plan.get(current_date, 0) + expense.amount
    return payment_plan

def get_sorted_payment_plan(payment_plan):
    """
    Given a dictionary of payment plan where keys are dates and values are decimals,
    return a list of lists where lists are key value pairs and sorted by dates.
    """
    new_payment_plan = []
    for key, value in payment_plan.items():
        new_payment_plan.append([key, value])
    return sorted(new_payment_plan)

def convert_payment_plan_dates(payment_plan):
    """
    Given a payment plan, converts date objects to str object in '%Y-%m-%d' format.
    """
    for item in payment_plan:
        item[0] = item[0].strftime("%Y-%m-%d")


def get_credit_card_payment_plan(card):
    """
    Given a card, returns a monthly payment plan dictionary.
    """
    payment_plan = {}
    incomplete_expenses = card.transactions.filter(due_date__gt=date.today())
    for expense in incomplete_expenses:
        add_installments_to_payment_plan(expense, payment_plan, card)
    sorted_payment_plan = get_sorted_payment_plan(payment_plan)
    convert_payment_plan_dates(sorted_payment_plan)
    return sorted_payment_plan

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
    categories = Category.objects.filter(Q(user=user, parent=parent, type=category_type)|Q(id=getattr(parent, 'id', None)))
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

def get_conversion_rate(from_currency, to_currency):
    """
    Calculates rate between currencies. Takes 2 currencies and returns a float. 
    """
    from_currency_rate = Rate.objects.get(currency=from_currency)
    to_currency_rate = Rate.objects.get(currency=to_currency)
    return to_currency_rate.rate / from_currency_rate.rate

def convert_money(from_currency, to_currency, amount):
    """
    A basic currency converter. Takes from currency, to currency and an amount.
    Returns converted amount.
    """
    conversion_rate = get_conversion_rate(from_currency, to_currency)
    return amount * conversion_rate

def get_transactions_currencies(qs):
    """
    Accepts a queryset of transactions and returns a set of currencies 
    which are of the accounts which transansactions made from.
    """
    currencies = qs.values_list('account__currency', flat=True)
    return Currency.objects.filter(id__in=set(currencies)).prefetch_related('rate')

def convert_category_stats(stats, from_currency, to_currency):
    for key, value in stats.items():
        value['sum'] = convert_money(from_currency, to_currency, value['sum'])
    return stats

def get_multi_currency_category_stats(qs, parent, user, target_currency=None):
    """
    Gets a qs of transactions, a category type, a parent category, a user and target currency. 
    Extracts and returns data to be used in category detail page.
    """
    category_stats = {}
    if not target_currency:
        target_currency = user.primary_currency

    categories = parent.get_descendants(include_self=True).annotate(
        sum=Sum(
            F('transactions__amount')/F('transactions__account__currency__rate__rate')*target_currency.get_rate(), 
            filter=Q(transactions__in=qs)
            )
    ).exclude(sum=None)

    for category in categories:
        try:
            category_stats[category.name]['sum'] += category.sum
        except KeyError:
            category_stats[category.name] = {'sum':category.sum, 'id':category.id}

    return category_stats

def get_multi_currency_category_json_stats(qs, parent, user, target_currency=None, card=False):
    """
    Gets a qs of transactions, a category type, a parent category, a user and target currency. 
    Extracts and returns data to be used in subcategory modal charts.
    """
    sum_data = []
    labels = []
    if not target_currency:
        target_currency = user.primary_currency
    if not card:
        categories = parent.get_descendants(include_self=True).annotate(
            sum=Sum(
                F('transactions__amount')/F('transactions__account__currency__rate__rate')*target_currency.get_rate(), 
                filter=Q(transactions__in=qs)
                )
        ).exclude(sum=None)
    else:
        categories = parent.get_descendants(include_self=True).annotate(
            sum=Sum(
                F('transactions__amount')/F('transactions__credit_card__currency__rate__rate')*target_currency.get_rate(), 
                filter=Q(transactions__in=qs)
                )
        ).exclude(sum=None)

    for category in categories:
        labels.append(category.name)
        if category.sum:
            sum_data.append(round(category.sum, 2))
    data = {
        "data": sum_data,
        "labels": labels,
    }
    return data

def get_multi_currency_main_category_stats(qs, category_type, user, target_currency=None):
    """
    Gets a qs of transactions, a category type, a user and target currency. 
    Extracts and returns data to be used in ins outs page.
    """
    category_stats = {}

    if not target_currency:
        target_currency = user.primary_currency

    categories = Category.objects.filter(user=user, type=category_type)

    categories_with_sum = categories.annotate(
        sum=Sum(
            F('transactions__amount')/F('transactions__account__currency__rate__rate')*target_currency.get_rate(), 
            filter=Q(transactions__in=qs)
            )
    ).exclude(sum=None)
    children_categories = Category.objects.filter(type=category_type, user=user, parent=None, is_transfer=False)
    for category in children_categories:
        for category_with_sum in categories_with_sum:
            if category.tree_id == category_with_sum.tree_id:
                try:
                    category_stats[category.name]['sum'] += category_with_sum.sum
                except KeyError:
                    category_stats[category.name] = {'sum':category_with_sum.sum, 'id':category.id}

    return category_stats

def get_category_detail_stats(qs, parent):
    categories = parent.get_descendants(include_self=True)
    category_stats = {}
    category_sums = categories.annotate(sum=Sum('transactions__amount', filter=Q(transactions__in=qs)))
    for category in category_sums:
        if not category.sum:
            continue
        category_stats[category.name] = {'sum': category.sum, "id": category.id}
    if not category_stats:
        category_stats["No data available"] = {"sum": 0, "id": 0}
    return category_stats

def add_category_stats(main_stats, added_stats):
    for key, value in added_stats.items():
        try:
            main_stats[key]['sum'] += value['sum']
        except KeyError:
            main_stats[key] = value

def get_multi_currency_category_detail_stats(qs, parent, to_currency):
    stats = {}
    currencies = get_transactions_currencies(qs)
    for currency in currencies:
        currency_transactions = qs.filter(account__currency=currency)
        category_stats = get_category_detail_stats(currency_transactions, parent)
        convert_category_stats(category_stats, currency, to_currency)
        add_category_stats(stats, category_stats)
    return stats 
        
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

def get_valid_date(year, month, day):
    """
    Accepts year, month and day values and returns the last day of month if 
    day is out of range of the month.
    Example: year=2004, month=2, day=31 will return date(2004, 2, 29)
    """
    try:
        return date(year, month, day)
    except ValueError:
        return get_valid_date(year, month, day-1)

def fill_missing_monthly_data(data):
    today = date.today()
    this_month = f"{today.year}-{today.month:02d}"
    start_date = min(data)
    end_date = max(max(data), this_month)
    current_date = start_date
    current_value = data[current_date]
    while current_date <= end_date:
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
        monthly_balance = fill_missing_monthly_data(monthly_balance)
        for key, value in monthly_balance.items():
            data[key] = data.get(key, 0) + value
    return sort_balance_data(data)

def get_user_currencies(user):
    """
    Takes a user and returns a set of user's active accounts.
    """
    currencies = set()
    active_user_accounts = Account.objects.filter(user=user, is_active=True).select_related('currency')
    for account in active_user_accounts:
        currencies.add(account.currency)
    return currencies


def get_worth_stats(user):
    stats = {}
    currencies = get_user_currencies(user)
    for currency in currencies:
        stats[currency] = get_monthly_currency_balance(user=user, currency=currency)
    return stats


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
    asset = transaction.content_object
    amount = transaction.amount
    if transaction.type == 'E':
        asset.balance += amount
    else:
        asset.balance -= amount
    asset.save()

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

def get_transaction_installment_due_date(transaction_date, installments, card):
    """
    Given a card, a transaction date and installments qty, calculates payment due date of the transaction.
    1. Find the next payment date using the transaction date
    2. Go to day 1 of the next payment date month
    3. Add installments qty months to that date
    4. Finds final payment date using card's get_next_payment_date method
    """
    next_payment_date = card.get_next_payment_date(transaction_date)
    first_day_of_month = date(next_payment_date.year, next_payment_date.month, 1)
    installments_months_later = first_day_of_month + relativedelta(months=int(installments)-1)
    due_date = card.get_next_payment_date(installments_months_later)
    return due_date

def create_transaction(data):
    '''
    Accepts a dictionary object, creates a transaction, edits related asset balance 
    and returns the created transaction object.
    '''
    with transaction.atomic():
        transaction_obj = Transaction.objects.create(**data)
        if isinstance(data['content_object'], CreditCard):
            installments = data.get('installments', None)
            if installments:
                transaction_obj.due_date = get_transaction_installment_due_date(data['date'], data['installments'], data['content_object'])
            else:
                transaction_obj.due_date = data['content_object'].next_payment_date
            transaction_obj.save()
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

def get_payment_transaction_data(form, asset):
    '''
    Accepts a Django form and asset string. Creates and returns a data dictionary 
    required for creating a transaction object.
    '''
    type = 'E' if asset=='account' else 'I'
    data = form.cleaned_data
    category = Category.objects.get(user=form.user, name='Pay Debt', type=type)
    transaction_data = {
        'content_object': data.get(asset),
        'name': 'Pay Debt',
        'amount': abs(data.get('amount')),
        'date': data.get('date'),
        'category': category,
        'type': type
    }
    return transaction_data

def handle_debt_payment(form, paid_asset):
    '''
    Accepts a Django form, creates transaction and transfer objects needed for loan payment process.
    '''
    with transaction.atomic():
        account_transaction = create_transaction(get_payment_transaction_data(form, asset='account'))
        paid_asset_transaction = create_transaction(get_payment_transaction_data(form, asset=paid_asset))
        Transfer.objects.create(
                user = form.user,
                from_transaction = account_transaction,
                to_transaction = paid_asset_transaction,
                date = account_transaction.date
            )

def handle_asset_delete(asset):
    '''
    Accepts an asset(account or loan) object and creates required transactions to zero account balance.
    '''
    if asset.balance > 0:
        category = Category.objects.get(user=asset.user, type='E', name='Asset Delete')
        data = {
            'content_object': asset,
            'name': 'Asset Delete',
            'amount': asset.balance,
            'category': category,
            'type': 'E',
            'installments': None
        }
        create_transaction(data)
    if asset.balance < 0:
        category = Category.objects.get(user=asset.user, type='I', name='Asset Delete')
        data = {
            'content_object': asset,
            'name': 'Asset Delete',
            'amount': asset.balance,
            'category': category,
            'type': 'I',
            'installments': None
        }
        create_transaction(data)

def handle_transfer_delete(transfer):
    '''
    Accepts a transfer object and calls handle_transaction_delete function with 
    object's from_transfer field object which will delete the transfer object, 
    all related transactions and withdraw account balances.
    '''
    handle_transaction_delete(transfer.from_transaction)

def edit_transaction(transaction, data):
    withdraw_asset_balance(transaction)
    for key, value in data.items():
        setattr(transaction, key, value)
    transaction.save()
    transaction.refresh_from_db()
    transaction.content_object.refresh_from_db()
    edit_asset_balance(transaction)

def handle_transfer_edit(object, data):
    from_transaction_data = {
        'content_object': data['from_account'],
        'amount': data['from_amount'],
        'date': data['date']
    }
    to_transaction_data = {
        'content_object': data['to_account'],
        'amount': data  ['to_amount'],
        'date': data['date']
    }
    with transaction.atomic():
        edit_transaction(object.from_transaction, from_transaction_data)
        edit_transaction(object.to_transaction, to_transaction_data)
        object.date = data['date']
        object.save()

def get_currency_ins_outs(currency, qs, user):
    currency_accounts_list = Account.objects.filter(user=user, currency=currency).values_list('id', flat=True)
    expense = qs.filter(
        content_type__model='account', 
        object_id__in=currency_accounts_list,
        type='E'
    ).aggregate(Sum('amount'))['amount__sum'] or 0 #aggregate returns a dictionary with 'amount__sum' key
    income = qs.filter(
        content_type__model='account', 
        object_id__in=currency_accounts_list,
        type='I'
    ).aggregate(Sum('amount'))['amount__sum'] or 0 #aggregate returns a dictionary with 'amount__sum' key
    currency_ins_outs = {
        'currency': currency,
        'expense': expense,
        'income': income,
        'balance': income-expense
    }
    return currency_ins_outs

def get_report_total(qs, target_currency):
    total = {
        'currency': target_currency.name,
        'expense': 0,
        'income': 0,
        'balance': 0
    }
    for currency in qs:
        rate = target_currency.rate.rate / currency.rate.rate
        total['expense'] += round(currency.expense * rate, 2)
        total['income'] += round(currency.income * rate, 2)
        total['balance'] += round(currency.balance * rate, 2)
    return total

def get_ins_outs_report(user, qs, target_currency=None):
    report = []
    if not target_currency:
        target_currency = user.primary_currency
    currencies = Currency.objects.filter(accounts__user=user).prefetch_related('rate').annotate(
        expense = Coalesce(Sum('accounts__transactions__amount', filter=Q(accounts__transactions__in=qs)&Q(accounts__transactions__type='E')), Decimal(0)),
        income = Coalesce(Sum('accounts__transactions__amount', filter=Q(accounts__transactions__in=qs)&Q(accounts__transactions__type='I')), Decimal(0))
    ).annotate(
        balance = F('income') - F('expense')
    )
    for currency in currencies:
        if currency.expense or currency.income:
            data = {
                'currency': currency,
                'expense': currency.expense,
                'income': currency.income,
                'balance': currency.balance
            }
            report.append(data)
    total = get_report_total(currencies, target_currency)
    return report, total

def create_guest_user():
    username = uuid.uuid4().hex
    email = f"{username}@example.com"
    password = "".join(random.sample(string.ascii_lowercase, 6))
    user = User.objects.create_user(
        username=username, email=email, password=password, is_guest=True
    )
    user.save()
    return user

def get_session_from_db(request):
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key
    request.session.set_expiry(86400) # will expire in 1 day
    return Session.objects.get(session_key=session_key)

def setup_guest_user(request):
    user = create_guest_user()
    login(request, user)
    session_obj = get_session_from_db(request)
    user_session = GuestUserSession.objects.create(user=user, session=session_obj)
    return user

@receiver(post_save, sender=User)
def create_user_categories(sender, instance, created, **kwargs):
    if created:
        create_categories(categories, instance)


@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    if created:
        UserPreferences.objects.create(user=instance)
