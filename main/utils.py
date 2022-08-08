from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, DecimalField
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save
from django.core.paginator import Paginator
from .models import User, UserPreferences, Account, Transfer, Category, Transaction, Loan
from .categories import categories
from datetime import date, timedelta


def get_latest_transactions(user, qty):
    accounts = Account.objects.filter(user=user)
    transactions = (
        Transaction.objects.filter(account__in=accounts)
        .exclude(category__is_transfer=True)
        .order_by("-date")[:qty]
    )
    return transactions


def get_latest_transfers(user, qty):
    transfers = (
        Transfer.objects.filter(user=user)
        .select_related(
            "from_transaction__account__currency", "to_transaction__account__currency"
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
    accounts = Account.objects.filter(user=user, is_active=True).select_related("currency")
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
    expences = qs.filter(type='E').aggregate(Sum("amount"))
    incomes = qs.filter(type='I').aggregate(Sum("amount"))
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
    object = get_object_or_404(model.objects.select_related('user'), id=id)
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


@receiver(post_save, sender=User)
def create_user_categories(sender, instance, created, **kwargs):
    if created:
        create_categories(categories, instance)


@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    if created:
        UserPreferences.objects.create(user=instance)
