import datetime
from .models import Account, Category, Transaction, Transfer, CreditCard
from .utils import (
    get_category_stats,
    get_comparison_stats,
    get_ins_outs_report,
    get_report_total,
    get_subcategory_stats,
    get_multi_currency_category_stats,
    get_multi_currency_main_category_stats,
    get_multi_currency_category_detail_stats,
    get_multi_currency_category_json_stats,
    get_stats,
    get_credit_card_payment_plan,
)
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.conf import settings
from django.db.models import Q


class TransactionsDateArchiveMixin(LoginRequiredMixin):
    model = Transaction
    date_field = "date"
    paginate_by = settings.DEFAULT_PAGINATION_QTY
    allow_future = True
    allow_empty = True
    extra_context = {
        "table_template": "main/table_transactions.html",
        "date": datetime.date.today(),
        "show_account": True
    }
    context_object_name = "transactions"
    template_name = "main/group_table_paginator.html"
    make_object_list = True
    month_format = "%m"

    def get_queryset(self):
        user_accounts_list = Account.objects.filter(
            user=self.request.user
        ).values_list("pk", flat=True)
        user_cards_list = CreditCard.objects.filter(
            user=self.request.user
        ).values_list("pk", flat=True)
        return (
            super()
            .get_queryset()
            .filter(
                # content_type__model="account", object_id__in=user_accounts_list
                Q(content_type__model="account") & Q(object_id__in=user_accounts_list) |
                Q(content_type__model="creditcard") & Q(object_id__in=user_cards_list)
            )
        )


class TransfersDateArchiveMixin(LoginRequiredMixin):
    model = Transfer
    date_field = "date"
    paginate_by = settings.DEFAULT_PAGINATION_QTY
    allow_future = True
    allow_empty = True
    extra_context = {
        "table_template": "main/table_transfers.html",
        "date": datetime.date.today(),
    }
    context_object_name = "transfers"
    template_name = "main/group_table_paginator.html"
    make_object_list = True
    month_format = "%m"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(user=self.request.user)
            .exclude(from_transaction__name="Pay Loan")
        )


class InsOutsDateArchiveMixin(LoginRequiredMixin):

    model = Transaction
    date_field = "date"
    paginate_by = settings.DEFAULT_PAGINATION_QTY
    allow_future = True
    allow_empty = True
    context_object_name = "transactions"
    template_name = "main/group_report_chart_script.html"
    extra_context = {"table_template": "main/table_transactions.html"}
    make_object_list = True
    month_format = "%m"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(account__user=self.request.user)
            .exclude(category__is_transfer=True)
            .select_related("category")
            .prefetch_related("content_object__currency")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = self.object_list
        expense_category_stats = get_multi_currency_main_category_stats(
            transactions, "E", self.request.user
        )
        income_category_stats = get_multi_currency_main_category_stats(
            transactions, "I", self.request.user
        )
        comparison_stats = get_comparison_stats(
            expense_category_stats, income_category_stats
        )
        report, total = get_ins_outs_report(
            self.request.user, transactions, self.request.user.primary_currency
        )

        extra_context = {
            "expense_stats": expense_category_stats,
            "income_stats": income_category_stats,
            "comparison_stats": comparison_stats,
            "report": report,
            "total": total,
        }
        context.update(extra_context)
        return context


class CategoryDateArchiveMixin(UserPassesTestMixin, LoginRequiredMixin):
    model = Transaction
    date_field = "date"
    paginate_by = settings.DEFAULT_PAGINATION_QTY
    allow_future = True
    allow_empty = True
    context_object_name = "transactions"
    template_name = "main/group_table_paginator_chart.html"
    month_format = "%m"
    make_object_list = True

    def test_func(self):
        return self.get_category().user == self.request.user

    def get_queryset(self):
        descendant_categories = self.get_category_descendants()
        return (
            super()
            .get_queryset()
            .filter(
                account__user=self.request.user,
                category__in=descendant_categories,
            )
            .exclude(category__is_transfer=True)
            .select_related("category")
            .prefetch_related("content_object__currency")
        )

    def get_category(self):
        category_id = self.kwargs.get("pk")
        self.category = get_object_or_404(Category, pk=category_id)
        return self.category

    def get_category_descendants(self):
        """
        returns a queryset of current category and it's descendants.
        """
        category = self.get_category()
        return category.get_descendants(include_self=True)

    def get_context_data(self, **kwargs):
        transactions = self.get_dated_items()[1]
        category_stats = get_multi_currency_category_stats(
            transactions, self.category, self.request.user
        )
        kwargs.update(
            {
                "category": self.category,
                "category_stats": category_stats,
                "date": datetime.date.today(),
                "table_template": "main/table_transactions.html",
                "show_category": True,
            }
        )
        return super().get_context_data(**kwargs)


class AccountDetailDateArchiveMixin(UserPassesTestMixin, LoginRequiredMixin):

    template_name = "main/group_account_bar_table_chart_script.html"
    model = Transaction
    date_field = "date"
    paginate_by = settings.DEFAULT_PAGINATION_QTY
    allow_future = True
    allow_empty = True
    context_object_name = "transactions"
    month_format = "%m"
    make_object_list = True

    def test_func(self):
        return self.account.user == self.request.user

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.set_account()

    def set_account(self):
        account_id = self.kwargs.get("pk")
        self.account = get_object_or_404(Account, id=account_id)
        if not self.account.is_active:
            raise Http404

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(account=self.account)
            .prefetch_related("content_object__currency")
        )

    def get_context_data(self, **kwargs):
        transactions = self.get_dated_items()[1]
        stats = get_stats(transactions, self.account.balance)
        expense_category_stats = get_category_stats(
            transactions, "E", None, self.request.user
        )
        income_category_stats = get_category_stats(
            transactions, "I", None, self.request.user
        )
        comparison_stats = get_comparison_stats(
            expense_category_stats, income_category_stats
        )
        context = {
            "account": self.account,
            "stats": stats,
            "expense_stats": expense_category_stats,
            "income_stats": income_category_stats,
            "comparison_stats": comparison_stats,
            "date": datetime.date.today(),
        }
        return super().get_context_data(**context)


class SubcategoryDateArchiveMixin(UserPassesTestMixin, LoginRequiredMixin):
    model = Transaction
    date_field = "date"
    allow_future = True
    allow_empty = True
    make_object_list = True
    month_format = "%m"

    def test_func(self):
        """Tests if parent category belongs to user."""
        category = self.get_category()
        return category.user == self.request.user

    def get_queryset(self):
        account = self.get_account()
        card = self.get_card()
        if account:
            return (
                super()
                .get_queryset()
                .filter(account=account)
                .exclude(category__is_transfer=True)
                .select_related("category")
                .prefetch_related("content_object__currency")
            )
        elif card:
            return (
                super()
                .get_queryset()
                .filter(credit_card=card)
                .exclude(category__is_transfer=True)
                .select_related("category")
                .prefetch_related("content_object__currency")
            )
        else:
            return (
                super()
                .get_queryset()
                .filter(account__user=self.request.user)
                .exclude(category__is_transfer=True)
                .select_related("category")
                .prefetch_related("content_object__currency")
            )

    def get_account(self):
        try:
            account_id = self.request.GET.get("account")
            account = Account.objects.get(id=account_id)
            if not account.is_active:
                raise Http404
            return account
        except:
            return None

    def get_card(self):
        try:
            card_id = self.request.GET.get("card")
            card = CreditCard.objects.get(id=card_id)
            if not card.is_active:
                raise Http404
            return card
        except: 
            return None

    def get_category(self):
        self.category = get_object_or_404(Category, pk=self.kwargs.get("pk"))
        return self.category

    def get(self, request, *args, **kwargs):
        qs = self.get_dated_items()[1]
        data = get_multi_currency_category_json_stats(
            qs, self.category, self.request.user, card=True
        )
        return JsonResponse(data)


class CreditCardDetailDateArchiveMixin(UserPassesTestMixin, LoginRequiredMixin):

    template_name = "main/group_table_paginator_chart_script.html"
    model = Transaction
    date_field = "date"
    paginate_by = settings.DEFAULT_PAGINATION_QTY
    allow_future = True
    allow_empty = True
    context_object_name = "transactions"
    month_format = "%m"
    make_object_list = True

    def test_func(self):
        return self.card.user == self.request.user

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.set_card()

    def set_card(self):
        card_id = self.kwargs.get("pk")
        self.card = get_object_or_404(CreditCard, id=card_id)
        if not self.card.is_active:
            raise Http404

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(credit_card=self.card)
            .prefetch_related("content_object__currency")
        )

    def get_context_data(self, **kwargs):
        transactions = self.get_dated_items()[1]
        expense_category_stats = get_category_stats(
            transactions, "E", None, self.request.user
        )
        payment_plan= get_credit_card_payment_plan(self.card)
        context = {
            "card": self.card,
            "expense_stats": expense_category_stats,
            "date": datetime.date.today(),
            "payment_plan": payment_plan,
        }
        return super().get_context_data(**context)