from django.contrib import admin
from .models import User, Currency, Account, ExpenseCategory, IncomeCategory, Income, Expense, Transfer, UserPreferences

# Register your models here.
admin.site.register(User)
admin.site.register(Currency)
admin.site.register(Account)
admin.site.register(ExpenseCategory)
admin.site.register(IncomeCategory)
admin.site.register(Expense)
admin.site.register(Income)
admin.site.register(Transfer)
admin.site.register(UserPreferences)