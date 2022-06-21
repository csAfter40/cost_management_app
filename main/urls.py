from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index' ),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('accounts', views.AccountsView.as_view(), name='accounts'),
    path('accounts/create', views.CreateAccountView.as_view(), name='create_account'),
    path('accounts/<pk>/edit', views.EditAccountView.as_view(), name='edit_account'),
    path('accounts/<pk>/del', views.DeleteAccountView.as_view(), name='delete_account'),
    path('categories', views.CategoriesView.as_view(), name='categories'),
    path('categories/expense/create', views.CreateExpenseCategory.as_view(), name='create_expense_category'),
    path('categories/income/create', views.CreateIncomeCategory.as_view(), name='create_income_category'),
    # path('categories/expense/create/<pk>', views.CreateExpenseSubcategory.as_view(), name='create_expense_subcategory'),
    # path('categories/income/create/<pk>', views.CreateIncomeSubcategory.as_view(), name='create_income_subcategory'),
    path('categories/expense/edit', views.EditExpenseCategory.as_view(), name='edit_expense_category'),
    path('categories/expense/del', views.DeleteExpenseCategory.as_view(), name='delete_expense_category'),
    path('categories/income/edit', views.EditIncomeCategory.as_view(), name='edit_income_category'),
    path('categories/income/del', views.DeleteIncomeCategory.as_view(), name='delete_income_category'),
    # path('transactions/expense', views.expense_input_view, name='expense_create'),
    # path('transactions/income', views.income_input_view, name='income_create'),
    # path('transactions/transfer', views.make_transfer_view, name='make_transfer'),
]

htmx_urlpatterns = [
    path('check_username', views.check_username, name='check_username'),
]

autocomplete_urlpatterns = [
    path('autocomplete/expense_name', views.expense_name_autocomplete, name='expense_name_autocomplete'),
    path('autocomplete/income_name', views.income_name_autocomplete, name='income_name_autocomplete'),
]

urlpatterns += htmx_urlpatterns
urlpatterns += autocomplete_urlpatterns