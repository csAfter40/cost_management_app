import json
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404
from django.urls import reverse, reverse_lazy
from .models import Account, Transfer, User, Transaction, Category
from .forms import ExpenseInputForm, IncomeInputForm, TransferForm
from .utils import get_latest_transactions, get_latest_transfers, get_account_data, validate_main_category_uniqueness, get_dates, get_stats, is_owner
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages

@login_required(login_url=reverse_lazy('main:login'))
def index(request): 
    transfer_form = TransferForm(user=request.user)
    expense_form = ExpenseInputForm(request.user)
    income_form = IncomeInputForm(request.user)

    if request.method == 'POST':
        # transfer form operations
        if request.POST.get('submit-transfer'):
            form = TransferForm(request.POST, user=request.user)
            if form.is_valid():
                data = form.cleaned_data
                date = data['date']
                from_account = data['from_account']
                to_account = data['to_account']
                from_amount = data['from_amount']
                to_amount = data['to_amount'] if data['to_amount'] else data['from_amount']
                
                with transaction.atomic():
                    from_transaction = Transaction(account=from_account, name='Transfer Out', amount=from_amount, date=date, type='TO')
                    from_account.balance -= from_amount
                    from_account.save()
                    from_transaction.save()
                    to_transaction = Transaction(account=to_account, name='Transfer In', amount=to_amount, date=date, type='TI')
                    to_account.balance += to_amount
                    to_account.save()
                    to_transaction.save()
                    transfer = Transfer(user=request.user, from_transaction=from_transaction, to_transaction=to_transaction, date=date)
                    transfer.save()

            else:
                transfer_form = form

        # expense form operations
        if request.POST.get('submit-expense'):
            form = ExpenseInputForm(request.user, request.POST)
            if form.is_valid():
                account = form.cleaned_data['account']
                amount = form.cleaned_data['amount']
                form.save()
                account.balance -= amount
                account.save()
                return HttpResponseRedirect(reverse('main:index'))
            else:
                expense_form = form
        #  income form operations
        if request.POST.get('submit-income'):
            form = IncomeInputForm(request.user, request.POST)
            if form.is_valid():
                account = form.cleaned_data['account']
                amount = form.cleaned_data['amount']
                form.save()
                account.balance += amount
                account.save()
                return HttpResponseRedirect(reverse('main:index'))
            else: income_form = form

    context = {
        'accounts': Account.objects.filter(user=request.user, is_active=True),
        'expense_form': expense_form,
        'income_form': income_form,
        'transfer_form': transfer_form,
        'transactions': get_latest_transactions(request.user, 5),
        'transfers': get_latest_transfers(request.user, 5),
        'account_data': get_account_data(request.user),
        'show_account': True,
    }
    return render(request, 'main/index.html', context)


def transaction_name_autocomplete(request):
    name_query = request.GET.get('name', None)
    type = request.GET.get('type', None)
    name_list = []
    if name_query:
        user = request.user
        accounts = Account.objects.filter(user=user, is_active=True)
        incomes = Transaction.objects.filter(account__in=accounts, name__icontains=name_query, type=type)
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
            login(request, user)
            next = request.POST.get('next', None)
            if next:
                return HttpResponseRedirect(next)
            return HttpResponseRedirect(reverse('main:index'))            
        messages.error(request, 'Invalid username or password.')
        return HttpResponseRedirect(reverse('main:login'))


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
            messages.error(request, 'Passwords must match!')
            return HttpResponseRedirect(reverse('main:register'))

        #Attempt create new user
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
        except IntegrityError as err:
            messages.error(request, 'Username already taken!')
            return HttpResponseRedirect(reverse('main:register'))
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

class AccountDetailView(UserPassesTestMixin, LoginRequiredMixin, View):
    
    def test_func(self):
        return is_owner(self.request.user, Account, self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):
        account_id = kwargs.get('pk')
        account = Account.objects.select_related('currency').get(id=account_id)
        transactions = Transaction.objects.filter(account=account).order_by('-date', '-created')
        stats = get_stats(transactions, account.balance)
        context = {
            'account': account,
            'transactions': transactions,
            'stats': stats,
        }
        if not account.is_active:
            raise Http404
        return render(request, 'main/account_detail.html', context)

    def put(self, request, *args, **kwargs):
        account_id = kwargs.get('pk')
        account = Account.objects.select_related('currency').get(id=account_id)
        data = json.loads(request.body)
        time = data['time']
        dates = get_dates()
        context = {}
        if time == 'all':
            context['transactions'] = Transaction.objects.filter(account=account).order_by('-date', '-created')
        elif time == 'week':
            print('week')
            context['transactions'] = Transaction.objects.filter(account=account, date__range=(dates['week_start'], dates['today'])).order_by('-date', '-created')
        elif time == 'month':
            context['transactions'] = Transaction.objects.filter(account=account, date__range=(dates['month_start'], dates['today'])).order_by('-date', '-created')
        elif time == 'year':
            context['transactions'] = Transaction.objects.filter(account=account, date__range=(dates['year_start'], dates['today'])).order_by('-date', '-created')
        context['stats'] = get_stats(context['transactions'], account.balance)
        context['account'] = account
        return render(request, 'main/account_detail_pack.html', context)


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

class EditAccountView(LoginRequiredMixin, UpdateView):
    
    model = Account
    fields = ['name', 'balance', 'currency']
    template_name = 'main/account_update.html'
    success_url = reverse_lazy('main:index')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user, is_active=True)



class DeleteAccountView(UserPassesTestMixin, LoginRequiredMixin, View):
    
    def test_func(self):
        self.account_id = self.request.POST['id']
        return is_owner(self.request.user, Account, self.account_id)

    def post(self, request):
        account = get_object_or_404(Account, id=self.account_id)
        account.is_active = False
        account.save()
        return HttpResponseRedirect(reverse('main:index'))


class CategoriesView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        context = {
            'expense_categories': Category.objects.filter(user=user, type='E'),
            'income_categories': Category.objects.filter(user=user, type='I'),
        }
        return render(request, 'main/categories.html', context)


class CreateExpenseCategory(UserPassesTestMixin, LoginRequiredMixin, View):
    
    def test_func(self):
        id = self.request.POST.get('category_id', None)
        if id:
            return is_owner(self.request.user, Category, id)
        else:
            return True

    def post(self, request):
        user = request.user
        name = request.POST['category_name']

        parent_id = request.POST.get('category_id', None)
        if parent_id:
            parent = get_object_or_404(Category, id=parent_id)
        else:
            if validate_main_category_uniqueness(name, user, type='E'):
                parent = None
            else:
                messages.error(request, f'There is already a {name} category in main categories.')
                return HttpResponseRedirect(reverse('main:categories'))

        new_category = Category(name=name, parent=parent, user=user, type='E')
        try:
            new_category.save()
        except IntegrityError:
            messages.error(request, f'There is already a {name} category under {parent.name} category.')
        return HttpResponseRedirect(reverse('main:categories'))


class CreateIncomeCategory(UserPassesTestMixin, LoginRequiredMixin, View):

    def test_func(self):
        id = self.request.POST.get('category_id', None)
        if id:
            return is_owner(self.request.user, Category, id)
        else:
            return True

    def post(self, request):
        user = request.user
        name = request.POST['category_name']
        parent_id = request.POST.get('category_id', None)
        if parent_id:
            parent = get_object_or_404(Category, id=parent_id)
        else:
            if validate_main_category_uniqueness(name, user, type='I'):
                parent = None
            else:
                messages.error(request, f'There is already a {name} category in main categories.')
                return HttpResponseRedirect(reverse('main:categories'))
        
        new_category = Category(name=name, parent=parent, user=user, type='I')
        try:
            new_category.save()
        except IntegrityError:
            messages.error(request, f'There is already a {name} category under {parent.name} category.')
        return HttpResponseRedirect(reverse('main:categories'))


class EditExpenseCategory(UserPassesTestMixin, LoginRequiredMixin, View):
    
    def test_func(self):
        return is_owner(self.request.user, Category, self.request.POST['category_id'])

    def post(self, request):
        id = request.POST['category_id']
        name = request.POST['category_name']
        category_obj = get_object_or_404(Category, id=id)
        category_obj.name = name
        if Category.objects.filter(parent=category_obj.parent, name=name).exists():
            if category_obj.parent:
                messages.error(request, f'There is already a {name} category under {category_obj.parent.name} category.')
            else:
                messages.error(request, f'There is already a {name} category in main categories.')
        else:
            category_obj.save()
        return HttpResponseRedirect(reverse('main:categories'))


class EditIncomeCategory(UserPassesTestMixin, LoginRequiredMixin, View):
    
    def test_func(self):
        return is_owner(self.request.user, Category, self.request.POST['category_id'])

    def post(self, request):
        id = request.POST['category_id']
        name = request.POST['category_name']
        category_obj = get_object_or_404(Category, id=id)
        category_obj.name = name
        if Category.objects.filter(parent=category_obj.parent, name=name).exists():
            if category_obj.parent:
                messages.error(request, f'There is already a {name} category under {category_obj.parent.name} category.')
            else:
                messages.error(request, f'There is already a {name} category in main categories.')
        else:
            category_obj.save()
        return HttpResponseRedirect(reverse('main:categories'))


class DeleteExpenseCategory(UserPassesTestMixin, LoginRequiredMixin, View):

    def test_func(self):
        return is_owner(self.request.user, Category, self.request.POST['category_id'])

    def post(self, request):
        id = request.POST['category_id']
        category = get_object_or_404(Category, id=id)
        category.delete()
        return HttpResponseRedirect(reverse('main:categories'))


class DeleteIncomeCategory(UserPassesTestMixin, LoginRequiredMixin, View):

    def test_func(self):
        return is_owner(self.request.user, Category, self.request.POST['category_id'])

    def post(self, request):
        id = request.POST['category_id']
        category = get_object_or_404(Category, id=id)
        category.delete()
        return HttpResponseRedirect(reverse('main:categories'))