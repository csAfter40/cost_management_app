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

    def test_login_url(self):
        self.assert_path_resolves_to_CBV("/login", views.LoginView, "login")

    def test_logout_url(self):
        self.assert_path_resolves_to_FBV("/logout", views.logout_view, "logout")

    def test_register_url(self):
        self.assert_path_resolves_to_CBV("/register", views.RegisterView, "register")

    def test_setup_url(self):
        self.assert_path_resolves_to_CBV("/setup", views.SetupView, "setup")

    def test_accounts_url(self):
        self.assert_path_resolves_to_CBV("/accounts", views.AccountsView, "accounts")

    def test_account_create_url(self):
        self.assert_path_resolves_to_CBV(
            "/accounts/create", views.CreateAccountView, "create_account"
        )

    def test_account_delete_url(self):
        self.assert_path_resolves_to_CBV(
            "/accounts/del/1", views.DeleteAccountView, "delete_account", pk=1
        )

    def test_account_detail_ajax_url(self):
        self.assert_path_resolves_to_CBV(
            "/accounts/1/ajax", views.AccountDetailAjaxView, "account_detail_ajax", pk=1
        )

    def test_account_detail_subcategory_ajax_url(self):
        self.assert_path_resolves_to_CBV(
            "/accounts/1/ajax/1",
            views.AccountDetailSubcategoryAjaxView,
            "account_detail_subcategory_ajax",
            pk=1,
            cat_pk=1,
        )

    def test_account_detail_url(self):
        self.assert_path_resolves_to_CBV(
            "/accounts/1", views.AccountDetailView, "account_detail", pk=1
        )

    def test_account_edit_url(self):
        self.assert_path_resolves_to_CBV(
            "/accounts/1/edit", views.EditAccountView, "edit_account", pk=1
        )

    def test_loans_url(self):
        self.assert_path_resolves_to_CBV("/loans", views.LoansView, "loans")

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

    def test_edit_transaction_url(self):
        self.assert_path_resolves_to_CBV("/transactions/1/edit", views.EditTransactionView, "edit_transaction", pk=1)

    def test_delete_transaction_url(self):
        self.assert_path_resolves_to_CBV('/transactions/1/delete', views.DeleteTransactionView, 'delete_transaction', pk=1)

    def test_delete_transfer_url(self):
        self.assert_path_resolves_to_CBV('/transfers/1/delete', views.DeleteTransferView, 'delete_transfer', pk=1)

    def test_transfers_url(self):
        self.assert_path_resolves_to_CBV('/transfers', views.TransfersView, 'transfers')
    
    def test_transfers_all_archive_url(self):
        self.assert_path_resolves_to_CBV('/transfers/date', views.TransfersAllArchiveView, 'transfers_all_archive')
    
    def test_transfers_year_archive_url(self):
        self.assert_path_resolves_to_CBV('/transfers/date/2001', views.TransfersYearArchiveView, 'transfers_year_archive', year=2001)
    
    def test_transfers_month_archive_url(self):
        self.assert_path_resolves_to_CBV('/transfers/date/2001/1', views.TransfersMonthArchiveView, 'transfers_month_archive', year=2001, month=1)
    