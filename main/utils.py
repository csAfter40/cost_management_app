from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import User, ExpenseCategory, IncomeCategory, UserPreferences
from .categories import expense_categories, income_categories

def create_categories(model, categories, user, parent=None):
    for key, value in categories.items():
        category = model.objects.create(name=key, slug=value['slug'], user=user)
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

@receiver(post_save, sender=User)
def create_user_categories(sender, instance, created, **kwargs):
    if created:
        create_categories(ExpenseCategory, expense_categories, instance)
        create_categories(IncomeCategory, income_categories, instance)

@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    if created:
        UserPreferences.objects.create(user=instance)