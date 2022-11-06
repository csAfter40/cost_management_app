import datetime
from .models import Account, Category
from .utils import (
    get_category_stats, 
    get_comparison_stats, 
    get_ins_outs_report, 
    get_report_total,
    get_subcategory_stats,
    get_multi_currency_category_stats,
    get_multi_currency_main_category_stats,
    get_multi_currency_category_detail_stats,
)
from django.shortcuts import get_object_or_404
from django.http import JsonResponse


class InsOutsDateArchiveMixin():
    def get_queryset(self):
        return super().get_queryset().filter(
            account__user=self.request.user
            ).exclude(category__is_transfer=True
            ).select_related('category').prefetch_related('content_object__currency')

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
        report, total = get_ins_outs_report(self.request.user, transactions, self.request.user.primary_currency)

        extra_context = {
            "expense_stats": expense_category_stats,
            "income_stats": income_category_stats,
            "comparison_stats": comparison_stats,
            "report": report,
            "total": total
        }
        context.update(extra_context)
        return context


class CategoryDateArchiveMixin():
    def get_queryset(self):
        descendant_categories = self.get_category_descendants()
        return super().get_queryset().filter(
            account__user=self.request.user, category__in=descendant_categories
            ).exclude(category__is_transfer=True
            ).select_related('category').prefetch_related('content_object__currency')

    def get_category(self):
        category_id = self.kwargs.get("pk")
        self.category = get_object_or_404(Category, pk=category_id)
        return self.category

    def get_category_descendants(self):
        '''
        returns a queryset of current category and it's descendants.
        '''
        category = self.get_category()
        return category.get_descendants(include_self=True)

    def get_context_data(self, **kwargs):
        transactions = self.get_dated_items()[1]
        category_stats = get_multi_currency_category_stats(
            transactions, self.category, self.request.user
        )
        kwargs.update({
            'category': self.category,
            'category_stats': category_stats,
            'date': datetime.date.today(),
            'table_template': 'main/table_transactions.html',
            'show_category': True,
        })
        return super().get_context_data(**kwargs)
