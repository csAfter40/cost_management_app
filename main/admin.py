from django.contrib import admin
from .models import User, Currency, Account, CostCategory, IncomeCategory, Income, Cost, Transfer, UserPreferences

# Register your models here.
admin.site.register(User)
admin.site.register(Currency)
admin.site.register(Account)
admin.site.register(CostCategory)
admin.site.register(IncomeCategory)
admin.site.register(Cost)
admin.site.register(Income)
admin.site.register(Transfer)
admin.site.register(UserPreferences)