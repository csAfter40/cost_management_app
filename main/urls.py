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
    path("profile", views.ProfileView.as_view(), name="profile"),
    path("profile/update", views.UpdateProfileView.as_view(), name="update_profile"),
    path("get_assets/account", views.GetAccountsView.as_view(), name="get_accounts"),
    path("get_assets/card", views.GetCreditCardsView.as_view(), name="get_credit_cards"),
    path("accounts", views.AccountsView.as_view(), name="accounts"),
    path("accounts/list", views.AccountsListView.as_view(), name="accounts_list"),
    path("accounts/create", views.CreateAccountView.as_view(), name="create_account"),
    path(
        "accounts/del/<int:pk>",
        views.DeleteAccountView.as_view(),
        name="delete_account",
    ),
    path("accounts/<int:pk>", views.AccountDetailView.as_view(), name="account_detail"),
    path("accounts/<int:pk>/date", views.AccountDetailAllArchiveView.as_view(), name="account_all_archive"),
    path("accounts/<int:pk>/date/<int:year>", views.AccountDetailYearArchiveView.as_view(), name="account_year_archive"),
    path("accounts/<int:pk>/date/<int:year>/<int:month>", views.AccountDetailMonthArchiveView.as_view(), name="account_month_archive"),
    path("accounts/<int:pk>/date/<int:year>/week/<int:week>", views.AccountDetailWeekArchiveView.as_view(), name="account_week_archive"),
    path("accounts/<int:pk>/date/<int:year>/<int:month>/<int:day>", views.AccountDetailDayArchiveView.as_view(), name="account_day_archive"),
    path(
        "accounts/<int:pk>/edit", views.EditAccountView.as_view(), name="edit_account"
    ),
    path("cards", views.CreditCardsView.as_view(), name="credit_cards"),
    path("cards/list", views.CreditCardsListView.as_view(), name="credit_cards_list"),
    path("cards/create", views.CreateCreditCardView.as_view(), name="create_credit_card"),
    path("cards/pay", views.PayCreditCardView.as_view(), name="pay_credit_card"),
    path("cards/<int:pk>", views.CreditCardDetailView.as_view(), name="credit_card_detail"),
    path("cards/<int:pk>/edit", views.EditCreditCardView.as_view(), name="edit_credit_card"),
    path("cards/del/<int:pk>", views.DeleteCreditCardView.as_view(), name="delete_credit_card"),
    path("loans", views.LoansView.as_view(), name="loans"),
    path("loans/list", views.LoansListView.as_view(), name="loans_list"),
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
    path(
        "categories/<int:pk>",
        views.CategoryDetailView.as_view(),
        name="category_detail",
    ),
    path(
        "categories/<int:pk>/date",
        views.CategoryAllArchiveView.as_view(),
        name="category_all_archive",
    ),
    path(
        'categories/<int:pk>/date/<int:year>',
        views.CategoryYearArchiveView.as_view(),
        name='category_year_archive'
    ),
    path(
        'categories/<int:pk>/date/<int:year>/<int:month>',
        views.CategoryMonthArchiveView.as_view(),
        name='category_month_archive'
    ),
    path(
        'categories/<int:pk>/date/<int:year>/week/<int:week>',
        views.CategoryWeekArchiveView.as_view(),
        name='category_week_archive'
    ),
    path(
        'categories/<int:pk>/date/<int:year>/<int:month>/<int:day>',
        views.CategoryDayArchiveView.as_view(),
        name='category_day_archive'
    ),
    path(
        'subcategories/<int:pk>/date',
        views.SubcategoryStatsAllArchiveView.as_view(),
        name='subcategory_all_archive'
    ),
    path(
        'subcategories/<int:pk>/date/<int:year>',
        views.SubcategoryStatsYearArchiveView.as_view(),
        name='subcategory_year_archive'
    ),
    path(
        'subcategories/<int:pk>/date/<int:year>/<int:month>',
        views.SubcategoryStatsMonthArchiveView.as_view(),
        name='subcategory_month_archive'
    ),
    path(
        'subcategories/<int:pk>/date/<int:year>/week/<int:week>',
        views.SubcategoryStatsWeekArchiveView.as_view(),
        name='subcategory_week_archive'
    ),
    path(
        'subcategories/<int:pk>/date/<int:year>/<int:month>/<int:day>',
        views.SubcategoryStatsDayArchiveView.as_view(),
        name='subcategory_day_archive'
    ),
    path("worth", views.WorthView.as_view(), name="worth"),
    path(
        'transactions',
        views.TransactionsView.as_view(),
        name='transactions'
    ),
    path(
        'transactions/date',
        views.TransactionsAllArchiveView.as_view(),
        name='transactions_all_archive'
    ),
    path(
        'transactions/date/<int:year>',
        views.TransactionsYearArchiveView.as_view(),
        name='transactions_year_archive'
    ),
    path(
        'transactions/date/<int:year>/<int:month>',
        views.TransactionsMonthArchiveView.as_view(),
        name='transactions_month_archive'
    ),
    path(
        'transactions/date/<int:year>/week/<int:week>',
        views.TransactionsWeekArchiveView.as_view(),
        name='transactions_week_archive'
    ),
    path(
        'transactions/date/<int:year>/<int:month>/<int:day>',
        views.TransactionsDayArchiveView.as_view(),
        name='transactions_day_archive'
    ),
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
    path(
        'ins_outs',
        views.InsOutsView.as_view(),
        name='ins_outs'
    ),
    path(
        'ins_outs/date',
        views.InsOutsAllArchiveView.as_view(),
        name='ins_outs_all_archive'
    ),
    path(
        'ins_outs/date/<int:year>',
        views.InsOutsYearArchiveView.as_view(),
        name='ins_outs_year_archive'
    ),
    path(
        'ins_outs/date/<int:year>/<int:month>',
        views.InsOutsMonthArchiveView.as_view(),
        name='ins_outs_month_archive'
    ),
    path(
        'ins_outs/date/<int:year>/week/<int:week>',
        views.InsOutsWeekArchiveView.as_view(),
        name='ins_outs_week_archive'
    ),
    path(
        'ins_outs/date/<int:year>/<int:month>/<int:day>',
        views.InsOutsDayArchiveView.as_view(),
        name='ins_outs_day_archive'
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
