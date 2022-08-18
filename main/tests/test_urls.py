from django.test.testcases import TestCase, SimpleTestCase
from django.urls import resolve
from main import views

class TestUrls(SimpleTestCase):

    def test_index(self):
        found = resolve('/')
        self.assertEquals(found.func, views.index)

    def test_login(self):
        found = resolve('/login')
        self.assertEquals(
            found.func.__name__, 
            views.LoginView.as_view().__name__
        )

    def test_logout(self):
        found = resolve('/logout')
        self.assertEquals(found.func, views.logout_view)

    def test_register(self):
        found = resolve('/register')
        self.assertEquals(
            found.func.__name__, 
            views.RegisterView.as_view().__name__
        )
    
    def test_accounts(self):
        found = resolve('/accounts')
        self.assertEquals(
            found.func.__name__, 
            views.AccountsView.as_view().__name__
        )

    