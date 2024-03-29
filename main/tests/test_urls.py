from django.test.testcases import SimpleTestCase
from django.urls import resolve, reverse
from main import views


class TestUrls(SimpleTestCase):
    def assert_path_resolves_to_CBV(self, path, view_class, name, *args, **kwargs):
        """
        Helper function for urls which has class based views.
        Asserts url resolves to view class.
        Asserts reverse of url name equals to url.
        """
        found = resolve(path)
        self.assertEquals(found.func.__name__, view_class.as_view().__name__)
        self.assertEquals(reverse(f"main:{name}", kwargs=kwargs), path)

    def assert_path_resolves_to_FBV(self, path, view_func, name, *args, **kwargs):
        """
        Helper function for urls which has function based views.
        Asserts url resolves to view class.
        Asserts reverse of url name equals to url.
        """
        found = resolve(path)
        self.assertEquals(found.func, view_func)
        self.assertEquals(reverse(f"main:{name}", kwargs=kwargs), path)

    def test_index_url(self):
        self.assert_path_resolves_to_FBV("/", views.index, "index")
    
    def test_main_url(self):
        self.assert_path_resolves_to_FBV("/main", views.main, "main")
    
    def test_test_drive_url(self):
        self.assert_path_resolves_to_FBV("/test_drive", views.test_drive, "test_drive")

    def test_login_url(self):
        self.assert_path_resolves_to_CBV("/login", views.LoginView, "login")

    def test_logout_url(self):
        self.assert_path_resolves_to_FBV("/logout", views.logout_view, "logout")

    def test_register_url(self):
        self.assert_path_resolves_to_CBV("/register", views.RegisterView, "register")

    def test_setup_url(self):
        self.assert_path_resolves_to_CBV("/setup", views.SetupView, "setup")

    def test_profile_url(self):
        self.assert_path_resolves_to_CBV("/profile", views.ProfileView, "profile")

    def test_update_profile_url(self):
        self.assert_path_resolves_to_CBV("/profile/update", views.UpdateProfileView, "update_profile")

    def test_get_accounts_url(self):
        self.assert_path_resolves_to_CBV("/get_assets/account", views.GetAccountsView, "get_accounts")

    def test_get_cards_url(self):
        self.assert_path_resolves_to_CBV("/get_assets/card", views.GetCreditCardsView, "get_credit_cards")

    def test_accounts_url(self):
        self.assert_path_resolves_to_CBV("/accounts", views.AccountsView, "accounts")

    def test_accounts_list_url(self):
        self.assert_path_resolves_to_CBV("/accounts/list", views.AccountsListView, "accounts_list")

    def test_account_create_url(self):
        self.assert_path_resolves_to_CBV(
            "/accounts/create", views.CreateAccountView, "create_account"
        )

    def test_account_delete_url(self):
        self.assert_path_resolves_to_CBV(
            "/accounts/del/1", views.DeleteAccountView, "delete_account", pk=1
        )

    def test_account_detail_url(self):
        self.assert_path_resolves_to_CBV(
            "/accounts/1", views.AccountDetailView, "account_detail", pk=1
        )
    
    def test_account_all_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/accounts/1/date", views.AccountDetailAllArchiveView, "account_all_archive", pk=1
        )
    
    def test_account_year_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/accounts/1/date/2001", views.AccountDetailYearArchiveView, "account_year_archive", pk=1, year=2001
        )
    
    def test_account_month_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/accounts/1/date/2001/2", views.AccountDetailMonthArchiveView, "account_month_archive", pk=1, year=2001, month=2
        )
    
    def test_account_week_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/accounts/1/date/2001/week/2", views.AccountDetailWeekArchiveView, "account_week_archive", pk=1, year=2001, week=2
        )
    
    def test_account_day_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/accounts/1/date/2001/2/1", views.AccountDetailDayArchiveView, "account_day_archive", pk=1, year=2001, month=2, day=1
        )

    def test_account_edit_url(self):
        self.assert_path_resolves_to_CBV(
            "/accounts/1/edit", views.EditAccountView, "edit_account", pk=1
        )

    def test_cards_url(self):
        self.assert_path_resolves_to_CBV("/cards", views.CreditCardsView, "credit_cards")

    def test_cards_list_url(self):
        self.assert_path_resolves_to_CBV("/cards/list", views.CreditCardsListView, "credit_cards_list")

    def test_cards_create_url(self):
        self.assert_path_resolves_to_CBV("/cards/create", views.CreateCreditCardView, "create_credit_card")

    def test_cards_pay_url(self):
        self.assert_path_resolves_to_CBV("/cards/pay", views.PayCreditCardView, "pay_credit_card")

    def test_cards_detail_url(self):
        self.assert_path_resolves_to_CBV("/cards/1", views.CreditCardDetailView, "credit_card_detail", pk=1)

    def test_credit_card_all_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/cards/1/date", views.CreditCardDetailAllArchiveView, "credit_card_all_archive", pk=1
        )
    
    def test_credit_card_year_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/cards/1/date/2001", views.CreditCardDetailYearArchiveView, "credit_card_year_archive", pk=1, year=2001
        )
    
    def test_credit_card_month_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/cards/1/date/2001/2", views.CreditCardDetailMonthArchiveView, "credit_card_month_archive", pk=1, year=2001, month=2
        )
    
    def test_credit_card_week_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/cards/1/date/2001/week/2", views.CreditCardDetailWeekArchiveView, "credit_card_week_archive", pk=1, year=2001, week=2
        )
    
    def test_credit_card_day_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/cards/1/date/2001/2/1", views.CreditCardDetailDayArchiveView, "credit_card_day_archive", pk=1, year=2001, month=2, day=1
        )

    def test_cards_edit_url(self):
        self.assert_path_resolves_to_CBV("/cards/1/edit", views.EditCreditCardView, "edit_credit_card", pk=1)

    def test_cards_edit_url(self):
        self.assert_path_resolves_to_CBV("/cards/del/1", views.DeleteCreditCardView, "delete_credit_card", pk=1)

    def test_loans_url(self):
        self.assert_path_resolves_to_CBV("/loans", views.LoansView, "loans")

    def test_loans_list_url(self):
        self.assert_path_resolves_to_CBV("/loans/list", views.LoansListView, "loans_list")

    def test_loan_create_url(self):
        self.assert_path_resolves_to_CBV(
            "/loans/create", views.CreateLoanView, "create_loan"
        )

    def test_loan_delete_url(self):
        self.assert_path_resolves_to_CBV(
            "/loans/del/1", views.DeleteLoanView, "delete_loan", pk=1
        )

    def test_loan_pay_url(self):
        self.assert_path_resolves_to_CBV("/loans/pay", views.PayLoanView, "pay_loan")

    def test_loan_detail_url(self):
        self.assert_path_resolves_to_CBV(
            "/loans/1", views.LoanDetailView, "loan_detail", pk=1
        )

    def test_loan_edit_url(self):
        self.assert_path_resolves_to_CBV(
            "/loans/1/edit", views.EditLoanView, "edit_loan", pk=1
        )

    def test_categories_url(self):
        self.assert_path_resolves_to_CBV(
            "/categories", views.CategoriesView, "categories"
        )

    def test_category_detail_url(self):
        self.assert_path_resolves_to_CBV(
            "/categories/1", views.CategoryDetailView, "category_detail", pk=1
        )

    def test_category_all_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/categories/1/date", views.CategoryAllArchiveView, "category_all_archive", pk=1
        )
    
    def test_category_year_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/categories/1/date/2001", views.CategoryYearArchiveView, "category_year_archive", pk=1, year=2001
        )
    
    def test_category_month_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/categories/1/date/2001/1", views.CategoryMonthArchiveView, "category_month_archive", pk=1, year=2001, month=1
        )
    
    def test_category_week_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/categories/1/date/2001/week/1", views.CategoryWeekArchiveView, "category_week_archive", pk=1, year=2001, week=1
        )

    def test_category_day_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/categories/1/date/2001/1/1", views.CategoryDayArchiveView, "category_day_archive", pk=1, year=2001, month=1, day=1
        )

    def test_subcategory_stats_all_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/subcategories/1/date", views.SubcategoryStatsAllArchiveView, "subcategory_all_archive", pk=1
        )

    def test_subcategory_stats_year_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/subcategories/1/date/2001", views.SubcategoryStatsYearArchiveView, "subcategory_year_archive", pk=1, year=2001
        )

    def test_subcategory_stats_month_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/subcategories/1/date/2001/1", views.SubcategoryStatsMonthArchiveView, "subcategory_month_archive", pk=1, year=2001, month=1
        )

    def test_subcategory_stats_week_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/subcategories/1/date/2001/week/1", views.SubcategoryStatsWeekArchiveView, "subcategory_week_archive", pk=1, year=2001, week=1
        )

    def test_subcategory_stats_day_archive_url(self):
        self.assert_path_resolves_to_CBV(
            "/subcategories/1/date/2001/1/1", views.SubcategoryStatsDayArchiveView, "subcategory_day_archive", pk=1, year=2001, month=1, day=1
        )

    def test_expense_category_create_url(self):
        self.assert_path_resolves_to_CBV(
            "/categories/expense/create",
            views.CreateExpenseCategory,
            "create_expense_category",
        )

    def test_income_category_create_url(self):
        self.assert_path_resolves_to_CBV(
            "/categories/income/create",
            views.CreateIncomeCategory,
            "create_income_category",
        )

    def test_edit_expense_category_url(self):
        self.assert_path_resolves_to_CBV(
            "/categories/expense/edit",
            views.EditExpenseCategory,
            "edit_expense_category",
        )

    def test_delete_expense_category_url(self):
        self.assert_path_resolves_to_CBV(
            "/categories/expense/del/1",
            views.DeleteExpenseCategory,
            "delete_expense_category",
            pk=1
        )

    def test_edit_income_category_url(self):
        self.assert_path_resolves_to_CBV(
            "/categories/income/edit", views.EditIncomeCategory, "edit_income_category"
        )

    def test_delete_income_category_url(self):
        self.assert_path_resolves_to_CBV(
            "/categories/income/del/1",
            views.DeleteIncomeCategory,
            "delete_income_category",
            pk=1
        )

    def test_check_username_url(self):
        self.assert_path_resolves_to_FBV(
            "/check_username", views.check_username, "check_username"
        )

    def test_autocomplete_transaction_name_url(self):
        self.assert_path_resolves_to_FBV(
            "/autocomplete/transaction_name",
            views.transaction_name_autocomplete,
            "transaction_name_autocomplete",
        )

    def test_worth_url(self):
        self.assert_path_resolves_to_CBV("/worth", views.WorthView, "worth")

    def test_transactions_url(self):
        self.assert_path_resolves_to_CBV('/transactions', views.TransactionsView, 'transactions')
    
    def test_transactions_all_archive_url(self):
        self.assert_path_resolves_to_CBV('/transactions/date', views.TransactionsAllArchiveView, 'transactions_all_archive')
    
    def test_transactions_year_archive_url(self):
        self.assert_path_resolves_to_CBV('/transactions/date/2001', views.TransactionsYearArchiveView, 'transactions_year_archive', year=2001)

    def test_transactions_month_archive_url(self):
        self.assert_path_resolves_to_CBV('/transactions/date/2001/1', views.TransactionsMonthArchiveView, 'transactions_month_archive', year=2001, month=1)   
    
    def test_transactions_week_archive_url(self):
        self.assert_path_resolves_to_CBV('/transactions/date/2001/week/1', views.TransactionsWeekArchiveView, 'transactions_week_archive', year=2001, week=1)
    
    def test_transactions_day_archive_url(self):
        self.assert_path_resolves_to_CBV('/transactions/date/2001/1/1', views.TransactionsDayArchiveView, 'transactions_day_archive', year=2001, month=1, day=1)

    def test_edit_transaction_url(self):
        self.assert_path_resolves_to_CBV("/transactions/1/edit", views.EditTransactionView, "edit_transaction", pk=1)

    def test_delete_transaction_url(self):
        self.assert_path_resolves_to_CBV('/transactions/1/delete', views.DeleteTransactionView, 'delete_transaction', pk=1)

    def test_delete_transfer_url(self):
        self.assert_path_resolves_to_CBV('/transfers/1/delete', views.DeleteTransferView, 'delete_transfer', pk=1)
    
    def test_edit_transfer_url(self):
        self.assert_path_resolves_to_CBV('/transfers/1/edit', views.EditTransferView, 'edit_transfer', pk=1)

    def test_transfers_url(self):
        self.assert_path_resolves_to_CBV('/transfers', views.TransfersView, 'transfers')
    
    def test_transfers_all_archive_url(self):
        self.assert_path_resolves_to_CBV('/transfers/date', views.TransfersAllArchiveView, 'transfers_all_archive')
    
    def test_transfers_year_archive_url(self):
        self.assert_path_resolves_to_CBV('/transfers/date/2001', views.TransfersYearArchiveView, 'transfers_year_archive', year=2001)
    
    def test_transfers_month_archive_url(self):
        self.assert_path_resolves_to_CBV('/transfers/date/2001/1', views.TransfersMonthArchiveView, 'transfers_month_archive', year=2001, month=1)
    
    def test_transfers_week_archive_url(self):
        self.assert_path_resolves_to_CBV('/transfers/date/2001/week/1', views.TransfersWeekArchiveView, 'transfers_week_archive', year=2001, week=1)
    
    def test_transfers_day_archive_url(self):
        self.assert_path_resolves_to_CBV('/transfers/date/2001/1/1', views.TransfersDayArchiveView, 'transfers_day_archive', year=2001, month=1, day=1)
    
    def test_ins_outs_url(self):
        self.assert_path_resolves_to_CBV('/ins_outs', views.InsOutsView, 'ins_outs')
    
    def test_ins_outs_all_archive_url(self):
        self.assert_path_resolves_to_CBV('/ins_outs/date', views.InsOutsAllArchiveView, 'ins_outs_all_archive')

    def test_ins_outs_year_archive_url(self):
        self.assert_path_resolves_to_CBV('/ins_outs/date/2001', views.InsOutsYearArchiveView, 'ins_outs_year_archive', year=2001)
    
    def test_ins_outs_month_archive_url(self):
        self.assert_path_resolves_to_CBV('/ins_outs/date/2001/1', views.InsOutsMonthArchiveView, 'ins_outs_month_archive', year=2001, month=1)
    
    def test_ins_outs_week_archive_url(self):
        self.assert_path_resolves_to_CBV('/ins_outs/date/2001/week/1', views.InsOutsWeekArchiveView, 'ins_outs_week_archive', year=2001, week=1)

    def test_ins_outs_day_archive_url(self):
        self.assert_path_resolves_to_CBV('/ins_outs/date/2001/1/1', views.InsOutsDayArchiveView, 'ins_outs_day_archive', year=2001, month=1, day=1)