from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.index, name="index"),
    path("main", views.main, name="main"),
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.RegisterView.as_view(), name="register"),
    path("setup", views.SetupView.as_view(), name="setup"),
    path("accounts", views.AccountsView.as_view(), name="accounts"),
    path("accounts/create", views.CreateAccountView.as_view(), name="create_account"),
    path(
        "accounts/del/<int:pk>",
        views.DeleteAccountView.as_view(),
        name="delete_account",
    ),
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
    path("loans/del/<int:pk>", views.DeleteLoanView.as_view(), name="delete_loan"),
    path(
        "loans/<int:pk>/ajax",
        views.LoanDetailAjaxView.as_view(),
        name="loan_detail_ajax",
    ),
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
    path(
        "categories/expense/edit",
        views.EditExpenseCategory.as_view(),
        name="edit_expense_category",
    ),
    path(
        "categories/expense/del/<int:pk>",
        views.DeleteExpenseCategory.as_view(),
        name="delete_expense_category",
    ),
    path(
        "categories/income/edit",
        views.EditIncomeCategory.as_view(),
        name="edit_income_category",
    ),
    path(
        "categories/income/del/<int:pk>",
        views.DeleteIncomeCategory.as_view(),
        name="delete_income_category",
    ),
    path("worth", views.WorthView.as_view(), name="worth"),
    path(
        "transactions/<int:pk>/edit",
        views.EditTransactionView.as_view(),
        name="edit_transaction",
    ),
    path(
        "transactions/<int:pk>/delete",
        views.DeleteTransactionView.as_view(),
        name="delete_transaction",
    ),
    path(
        'transfers',
        views.TransfersView.as_view(),
        name='transfers'
    ),
    path(
        'transfers/<int:pk>/delete',
        views.DeleteTransferView.as_view(),
        name='delete_transfer'
    ),
    path(
        'transfers/<int:pk>/edit',
        views.EditTransferView.as_view(),
        name='edit_transfer'
    ),
    path(
        'transfers/date',
        views.TransfersAllArchiveView.as_view(),
        name='transfers_all_archive'
    ),
    path(
        'transfers/date/<int:year>',
        views.TransfersYearArchiveView.as_view(),
        name='transfers_year_archive'
    ),
    path(
        'transfers/date/<int:year>/<int:month>',
        views.TransfersMonthArchiveView.as_view(),
        name='transfers_month_archive'
    ),
    path(
        'transfers/date/<int:year>/week/<int:week>',
        views.TransfersWeekArchiveView.as_view(),
        name='transfers_week_archive'
    ),
    path(
        'transfers/date/<int:year>/<int:month>/<int:day>',
        views.TransfersDayArchiveView.as_view(),
        name='transfers_day_archive'
    ),
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
