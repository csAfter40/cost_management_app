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

    def test_index(self):
        self.assert_path_resolves_to_FBV("/", views.index)

    def test_login(self):
        self.assert_path_resolves_to_CBV("/login", views.LoginView)

    def test_logout(self):
        self.assert_path_resolves_to_FBV("/logout", views.logout_view)

    def test_register(self):
        self.assert_path_resolves_to_CBV("/register", views.RegisterView)

    def test_accounts(self):
        self.assert_path_resolves_to_CBV("/accounts", views.AccountsView)

    def test_accounts_create(self):
        self.assert_path_resolves_to_CBV("/accounts/create", views.CreateAccountView)

    def test_accounts_delete(self):
        self.assert_path_resolves_to_CBV("/accounts/del/1", views.DeleteAccountView)
