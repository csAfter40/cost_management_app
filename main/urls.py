from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index' ),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('wallet', views.wallet, name='wallet'),
    path('accounts', views.AccountsView.as_view(), name='accounts'),
    path('accounts/create', views.CreateAccountView.as_view(), name='create_account'),
    path('accounts/<pk>/edit', views.EditAccountView.as_view(), name='edit_account'),
    path('accounts/<pk>/del', views.DeleteAccountView.as_view(), name='delete_account'),
    path('transactions/expense', views.expense_input_view, name='expense_create'),
    path('transactions/income', views.income_input_view, name='income_create'),
]

htmx_urlpatterns = [
    path('check_username', views.check_username, name='check_username'),
]

urlpatterns += htmx_urlpatterns