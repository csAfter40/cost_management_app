from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.RegisterView.as_view(), name="register"),
    path("accounts", views.AccountsView.as_view(), name="accounts"),
    path("accounts/create", views.CreateAccountView.as_view(), name="create_account"),
    path("accounts/del", views.DeleteAccountView.as_view(), name="delete_account"),
    path(
        "accounts/<int:pk>/ajax",
        views.AccountDetailAjaxView.as_view(),
        name="account_detail_ajax",
    ),
    path(
        "accounts/<int:pk>/ajax/<int:cat_pk>",
        views.AccountDetailSubcategoryAjaxView.as_view(),
        name="account_detail_subcategory_ajax",
    ),
    path("accounts/<int:pk>", views.AccountDetailView.as_view(), name="account_detail"),
    path(
        "accounts/<int:pk>/edit", views.EditAccountView.as_view(), name="edit_account"
    ),
    path("loans", views.LoansView.as_view(), name="loans"),
    path("loans/create", views.CreateLoanView.as_view(), name="create_loan"),
    path("loans/del", views.DeleteLoanView.as_view(), name="delete_loan"),
    path("loans/pay", views.PayLoanView.as_view(), name="pay_loan"),
    path("loans/<int:pk>", views.LoanDetailView.as_view(), name="loan_detail"),
    path("loans/<int:pk>/edit", views.EditLoanView.as_view(), name="edit_loan"),
    path("categories", views.CategoriesView.as_view(), name="categories"),
    path(
        "categories/expense/create",
        views.CreateExpenseCategory.as_view(),
        name="create_expense_category",
    ),
    path(
        "categories/income/create",
        views.CreateIncomeCategory.as_view(),
        name="create_income_category",
    ),
    # path('categories/expense/create/<pk>', views.CreateExpenseSubcategory.as_view(), name='create_expense_subcategory'),
    # path('categories/income/create/<pk>', views.CreateIncomeSubcategory.as_view(), name='create_income_subcategory'),
    path(
        "categories/expense/edit",
        views.EditExpenseCategory.as_view(),
        name="edit_expense_category",
    ),
    path(
        "categories/expense/del",
        views.DeleteExpenseCategory.as_view(),
        name="delete_expense_category",
    ),
    path(
        "categories/income/edit",
        views.EditIncomeCategory.as_view(),
        name="edit_income_category",
    ),
    path(
        "categories/income/del",
        views.DeleteIncomeCategory.as_view(),
        name="delete_income_category",
    ),
    # path('transactions/expense', views.expense_input_view, name='expense_create'),
    # path('transactions/income', views.income_input_view, name='income_create'),
    # path('transactions/transfer', views.make_transfer_view, name='make_transfer'),
]

htmx_urlpatterns = [
    path("check_username", views.check_username, name="check_username"),
]

autocomplete_urlpatterns = [
    path(
        "autocomplete/transaction_name",
        views.transaction_name_autocomplete,
        name="transaction_name_autocomplete",
    ),
]

urlpatterns += htmx_urlpatterns
urlpatterns += autocomplete_urlpatterns
