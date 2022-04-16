from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from requests import request
from .models import Account, Expense, User, ExpenseCategory, IncomeCategory, Income
from .forms import ExpenseInputForm, IncomeInputForm
from .utils import get_latest_transactions
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required

@login_required(login_url=reverse_lazy('main:login'))
def index(request): 
    expense_form = ExpenseInputForm(request.user)
    income_form = IncomeInputForm(request.user)

    context = {
        'accounts': Account.objects.filter(user=request.user),
        'expense_form': expense_form,
        'income_form': income_form,
        'transactions': get_latest_transactions(request.user, 5)
    }
    return render(request, 'main/index.html', context)

def expense_name_autocomplete(request):
    name_query = request.GET.get('name', None)
    name_list = []
    if name_query:
        user = request.user
        accounts = Account.objects.filter(user=user)
        expenses = Expense.objects.filter(account__in=accounts, name__icontains=name_query)
        for expense in expenses:
            name_list.append(expense.name)
    return JsonResponse({'status': 200, 'data': name_list})

def income_name_autocomplete(request):
    name_query = request.GET.get('name', None)
    name_list = []
    if name_query:
        user = request.user
        accounts = Account.objects.filter(user=user)
        incomes = Income.objects.filter(account__in=accounts, name__icontains=name_query)
        for income in incomes:
            name_list.append(income.name)
    return JsonResponse({'status': 200, 'data': name_list})

class LoginView(View):
    def get(self, request):
        return render(request, 'main/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                next = request.POST.get('next', None)
                if next:
                    return HttpResponseRedirect(next)
                return HttpResponseRedirect(reverse('main:index'))
            return render(request, 'main/login.html', {'message': 'User is not active!'})
        return render(request, 'main/login.html', {'message': 'Invalid username or password.'})


class RegisterView(View):
    def get(self, request):
        return render(request, 'main/register.html')

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']

        #Ensure password matches confirmation
        password = request.POST['password']
        confirmation = request.POST['confirmation']
        if password != confirmation:
            return render(request, 'main/register.html', {'message': 'Passwords must match!'})

        #Attempt create new user
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
        except IntegrityError:
            return render(request, 'main/register.html', {'message': 'Username already taken!'})
        login(request, user)
        return HttpResponseRedirect(reverse('main:index'))


def check_username(request, *args, **kwargs):
    username = request.POST.get('username')
    if len(username)>=3:
        if User.objects.filter(username=username).exists():
            return HttpResponse('<p class="mx-2 text-danger" id="username_check_text"><small><i class="bi bi-x-circle"></i> This username exists</small></p>')
        else:
            return HttpResponse('<p class="mx-2 text-success" id="username_check_text"><small><i class="bi bi-check2-circle"></i> This username is available</small></p>')
    else:
        return HttpResponse('<p class="text-muted mx-2" id="username_check_text"></p>')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('main:index'))


class AccountsView(ListView):
    pass

class CreateAccountView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('main:login')
    model = Account
    fields = ['name', 'balance', 'currency']
    success_url = reverse_lazy('main:index')
    template_name = 'main/create_account.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)

class EditAccountView(UpdateView):
    pass

class DeleteAccountView(DeleteView):
    pass


def expense_input_view(request):
    if request.method == 'POST':
        form = ExpenseInputForm(request.user, request.POST)

        if form.is_valid():
            account = form.cleaned_data['account']
            amount = form.cleaned_data['amount']
            form.save()
            account.balance -= amount
            account.save()
    
    return HttpResponseRedirect(reverse('main:index'))
            



def income_input_view(request):
    if request.method == 'POST':
        form = IncomeInputForm(request.user, request.POST)

        if form.is_valid():
            account = form.cleaned_data['account']
            amount = form.cleaned_data['amount']
            form.save()
            account.balance += amount
            account.save()
    
    return HttpResponseRedirect(reverse('main:index'))