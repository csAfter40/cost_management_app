from .models import Account, Category
from .utils import (
    get_category_stats, 
    get_comparison_stats, 
    get_ins_outs_report, 
    get_report_total,
    get_subcategory_stats
)
from django.shortcuts import get_object_or_404
from django.http import JsonResponse


class InsOutsDateArchiveMixin():
    def get_queryset(self):
        user_accounts_list = Account.objects.filter(user=self.request.user).values_list('pk', flat=True)
        user_transfer_categories = Category.objects.filter(user=self.request.user, is_transfer=True)
        return super().get_queryset().filter(
            content_type__model='account', 
            object_id__in=user_accounts_list
            ).exclude(category__in=user_transfer_categories)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = self.get_dated_items()[1]
        expense_category_stats = get_category_stats(
            transactions, "E", None, self.request.user
        )
        income_category_stats = get_category_stats(
            transactions, "I", None, self.request.user
        )
        comparison_stats = get_comparison_stats(
            expense_category_stats, income_category_stats
        )
        report = get_ins_outs_report(self.request.user, transactions)
        total = get_report_total(report, self.request.user.primary_currency)

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
        user_accounts_list = Account.objects.filter(user=self.request.user).values_list('pk', flat=True)
        user_transfer_categories = Category.objects.filter(user=self.request.user, is_transfer=True)
        descendant_categories = self.get_category_descendants()
        return super().get_queryset().filter(
            content_type__model='account', 
            object_id__in=user_accounts_list,
            category__in=descendant_categories
            ).exclude(category__in=user_transfer_categories)

    def get_category(self):
        category_id = self.kwargs.get("pk")
        return get_object_or_404(Category, pk=category_id)

    def get_category_descendants(self):
        '''
        returns a queryset of current category and it's descendants.
        '''
        category = self.get_category()
        return category.get_descendants(include_self=True)

    def get(self, request, *args, **kwargs):
        if request.GET.get('ajax', None):
            qs = self.get_dated_items()[1]
            category = self.get_category()
            data = get_subcategory_stats(qs, category)
            return JsonResponse(data)
        return super().get(request, *args, **kwargs)