from django.contrib import admin
from .models import (
    User,
    Currency,
    Account,
    Category,
    Transaction,
    Transfer,
    UserPreferences,
    Loan,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    ordering = ('username',)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol')
    ordering = ('code',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'type')
    ordering = ('user__username', 'type', 'name')


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_active')
    ordering = ('user__username', '-is_active', 'name')


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_active')
    ordering = ('user__username', '-is_active', 'name')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display= ('name', 'amount', 'account', 'date', 'get_user')
    ordering = ('-date',)

    def get_user(self, obj):
        return obj.account.user

    # sets column name as 'user' in admin panel. otherwise it was 'get_user'
    get_user.short_description = 'user'

@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('user', 'from_transaction', 'to_transaction', 'date')
    ordering = ('-date',)


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user',)
    ordering = ('user__username',)
