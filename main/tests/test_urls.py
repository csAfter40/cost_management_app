from django.test.testcases import SimpleTestCase
from django.urls import resolve
from main import views


class TestUrls(SimpleTestCase):
    def assert_path_resolves_to_CBV(self, path, view_class):
        found = resolve(path)
        self.assertEquals(found.func.__name__, view_class.as_view().__name__)

    def assert_path_resolves_to_FBV(self, path, view_func):
        found = resolve(path)
        self.assertEquals(found.func, view_func)

    def test_index_url(self):
        self.assert_path_resolves_to_FBV("/", views.index)

    def test_login_url(self):
        self.assert_path_resolves_to_CBV("/login", views.LoginView)

    def test_logout_url(self):
        self.assert_path_resolves_to_FBV("/logout", views.logout_view)

    def test_register_url(self):
        self.assert_path_resolves_to_CBV("/register", views.RegisterView)

    def test_accounts_url(self):
        self.assert_path_resolves_to_CBV("/accounts", views.AccountsView)

    def test_account_create_url(self):
        self.assert_path_resolves_to_CBV("/accounts/create", views.CreateAccountView)

    def test_account_delete_url(self):
        self.assert_path_resolves_to_CBV("/accounts/del/1", views.DeleteAccountView)

    def test_account_detail_ajax_url(self):
        self.assert_path_resolves_to_CBV(
            "/accounts/1/ajax/1", views.AccountDetailAjaxView
        )

    def test_account_detail_subcategory_ajax_url(self):
        self.assert_path_resolves_to_CBV(
            "/accounts/1/ajax/1", views.AccountDetailSubcategoryAjaxView
        )

    def test_account_detail_url(self):
        self.assert_path_resolves_to_CBV("/accounts/1", views.AccountDetailView)

    def test_account_edit_url(self):
        self.assert_path_resolves_to_CBV("/accounts/1/edit", views.EditAccountView)

    def test_loans_url(self):
        self.assert_path_resolves_to_CBV("/loans", views.LoansView)

    def test_loan_create_url(self):
        self.assert_path_resolves_to_CBV("/loans/create", views.CreateLoanView)

    def test_loan_delete_url(self):
        self.assert_path_resolves_to_CBV("/loans/del/1", views.DeleteLoanView)