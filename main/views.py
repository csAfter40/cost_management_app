from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import (
    CreateView, 
    UpdateView, 
    ListView, 
    DetailView, 
    DeleteView,
    FormView,
)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404
from django.urls import reverse, reverse_lazy
from .models import Account, Transfer, User, Transaction, Category, Loan
from .forms import ExpenseInputForm, IncomeInputForm, TransferForm, PayLoanForm
from .utils import (
    get_latest_transactions,
    get_latest_transfers,
    get_account_data,
    get_loan_data,
    get_subcategory_stats,
    validate_main_category_uniqueness,
    get_dates,
    get_stats,
    is_owner,
    get_category_stats,
    get_paginated_qs,
    get_comparison_stats,
    get_subcategory_stats,
)
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.conf import settings


@login_required(login_url=reverse_lazy("main:login"))
def index(request):
    transfer_form = TransferForm(user=request.user)
    expense_form = ExpenseInputForm(request.user)
    income_form = IncomeInputForm(request.user)

    if request.method == "POST":
        # transfer form operations
        if request.POST.get("submit-transfer"):
            form = TransferForm(request.POST, user=request.user)
            if form.is_valid():
                data = form.cleaned_data
                date = data["date"]
                from_account = data["from_account"]
                to_account = data["to_account"]
                from_amount = data["from_amount"]
                to_amount = (
                    data["to_amount"] if data["to_amount"] else data["from_amount"]
                )
                from_category = Category.objects.get(
                    user=request.user, name="Transfer Out"
                )
                to_category = Category.objects.get(
                    user=request.user, name="Transfer In"
                )

                with transaction.atomic():
                    from_transaction = Transaction(
                        account=from_account,
                        name="Transfer Out",
                        amount=from_amount,
                        date=date,
                        type="E",
                        category=from_category,
                    )
                    from_account.balance -= from_amount
                    from_account.save()
                    from_transaction.save()
                    to_transaction = Transaction(
                        account=to_account,
                        name="Transfer In",
                        amount=to_amount,
                        date=date,
                        type="I",
                        category=to_category,
                    )
                    to_account.balance += to_amount
                    to_account.save()
                    to_transaction.save()
                    transfer = Transfer(
                        user=request.user,
                        from_transaction=from_transaction,
                        to_transaction=to_transaction,
                        date=date,
                    )
                    transfer.save()
                return HttpResponseRedirect(reverse("main:index"))

            else:
                transfer_form = form

        # expense form operations
        if request.POST.get("submit-expense"):
            form = ExpenseInputForm(request.user, request.POST)
            if form.is_valid():
                account = form.cleaned_data["account"]
                amount = form.cleaned_data["amount"]
                form.save()
                account.balance -= amount
                account.save()
                return HttpResponseRedirect(reverse("main:index"))
            else:
                expense_form = form
        #  income form operations
        if request.POST.get("submit-income"):
            form = IncomeInputForm(request.user, request.POST)
            if form.is_valid():
                account = form.cleaned_data["account"]
                amount = form.cleaned_data["amount"]
                form.save()
                account.balance += amount
                account.save()
                return HttpResponseRedirect(reverse("main:index"))
            else:
                income_form = form

    context = {
        "accounts": Account.objects.filter(user=request.user, is_active=True),
        "loans": Loan.objects.filter(user=request.user, is_active=True),
        "expense_form": expense_form,
        "income_form": income_form,
        "transfer_form": transfer_form,
        "transactions": get_latest_transactions(request.user, 5),
        "transfers": get_latest_transfers(request.user, 5),
        "account_data": get_account_data(request.user),
        "show_account": True,
    }
    return render(request, "main/index.html", context)

@login_required
def transaction_name_autocomplete(request):
    name_query = request.GET.get("name", None)
    type = request.GET.get("type", None)
    name_list = []
    if name_query:
        user = request.user
        accounts = Account.objects.filter(user=user, is_active=True)
        incomes = Transaction.objects.filter(
            account__in=accounts, name__icontains=name_query, type=type
        )
        for income in incomes:
            name_list.append(income.name)
    return JsonResponse({"status": 200, "data": name_list})


class LoginView(View):
    def get(self, request):
        return render(request, "main/login.html")

    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            next = request.POST.get("next", None)
            if next:
                return HttpResponseRedirect(next)
            return HttpResponseRedirect(reverse("main:index"))
        messages.error(request, "Invalid username or password.")
        return HttpResponseRedirect(reverse("main:login"))


class RegisterView(View):
    def get(self, request):
        return render(request, "main/register.html")

    def post(self, request):
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, "Passwords must match!")
            return HttpResponseRedirect(reverse("main:register"))

        # Attempt create new user
        try:
            user = User.objects.create_user(
                username=username, email=email, password=password
            )
            user.save()
        except IntegrityError as err:
            messages.error(request, "Username already taken!")
            return HttpResponseRedirect(reverse("main:register"))
        login(request, user)
        return HttpResponseRedirect(reverse("main:index"))


def check_username(request, *args, **kwargs):
    username = request.POST.get("username")
    if len(username) >= 3:
        if User.objects.filter(username=username).exists():
            return HttpResponse(
                '<p class="mx-2 text-danger" id="username_check_text"><small><i class="bi bi-x-circle"></i> This username exists</small></p>'
            )
        else:
            return HttpResponse(
                '<p class="mx-2 text-success" id="username_check_text"><small><i class="bi bi-check2-circle"></i> This username is available</small></p>'
            )
    else:
        return HttpResponse('<p class="text-muted mx-2" id="username_check_text"></p>')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return HttpResponseRedirect(reverse("main:index"))


class AccountsView(LoginRequiredMixin, ListView):
    model = Account
    template_name = "main/accounts.html"

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user, is_active=True).select_related('currency')


class AccountDetailAjaxView(LoginRequiredMixin, DetailView):

    model = Account
    template_name = "main/account_detail_pack.html"
        
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_active:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        account = self.get_object()
        time = self.request.GET.get("time", "all")
        dates = get_dates()
        context = {}
        if time == "all":
            qs = Transaction.objects.filter(account=account).order_by(
                "-date", "-created"
            )
        elif time == "week":
            qs = Transaction.objects.filter(
                account=account, date__range=(dates["week_start"], dates["today"])
            ).order_by("-date", "-created")
        elif time == "month":
            qs = Transaction.objects.filter(
                account=account, date__range=(dates["month_start"], dates["today"])
            ).order_by("-date", "-created")
        elif time == "year":
            qs = Transaction.objects.filter(
                account=account, date__range=(dates["year_start"], dates["today"])
            ).order_by("-date", "-created")
        expense_category_stats = get_category_stats(qs, "E", None, self.request.user)
        income_category_stats = get_category_stats(qs, "I", None, self.request.user)
        comparison_stats = get_comparison_stats(
            expense_category_stats, income_category_stats
        )
        context = {
            "transactions": get_paginated_qs(qs, self.request, 10),
            "stats": get_stats(qs, account.balance),
            "account": account,
            "expense_stats": expense_category_stats,
            "income_stats": income_category_stats,
            "comparison_stats": comparison_stats,
        }
        return super().get_context_data(**context)


class AccountDetailSubcategoryAjaxView(LoginRequiredMixin, DetailView):
    
    model = Account

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user).select_related('currency')

    def get(self, request, *args, **kwargs):
        account = self.get_object()
        if not account.is_active:
            raise Http404
        category_id = kwargs.get("cat_pk")
        category = get_object_or_404(Category, id=category_id)
        time = self.request.GET.get("time")
        dates = get_dates()
        if time == "all":
            qs = Transaction.objects.filter(account=account).order_by(
                "-date", "-created"
            )
        elif time == "week":
            qs = Transaction.objects.filter(
                account=account, date__range=(dates["week_start"], dates["today"])
            ).order_by("-date", "-created")
        elif time == "month":
            qs = Transaction.objects.filter(
                account=account, date__range=(dates["month_start"], dates["today"])
            ).order_by("-date", "-created")
        elif time == "year":
            qs = Transaction.objects.filter(
                account=account, date__range=(dates["year_start"], dates["today"])
            ).order_by("-date", "-created")
        data = get_subcategory_stats(qs, category)

        return JsonResponse(data)


class AccountDetailView(LoginRequiredMixin, DetailView):

    model = Account

    def get(self, request, *args, **kwargs):
        account = self.get_object()
        if not account.is_active:
            raise Http404
        return super().get(request, *args, **kwargs)
        
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        account = self.get_object()
        transactions = Transaction.objects.filter(account=account).order_by(
            "-date", "-created"
        ).select_related('account__currency')
        stats = get_stats(transactions, account.balance)
        expense_category_stats = get_category_stats(
            transactions, "E", None, self.request.user
        )
        income_category_stats = get_category_stats(
            transactions, "I", None, self.request.user
        )
        comparison_stats = get_comparison_stats(
            expense_category_stats, income_category_stats
        )
        page_obj = get_paginated_qs(transactions, self.request, 10)

        context = {
            "account": account,
            "transactions": page_obj,
            "stats": stats,
            "expense_stats": expense_category_stats,
            "income_stats": income_category_stats,
            "comparison_stats": comparison_stats,
        }
        return super().get_context_data(**context)


class CreateAccountView(LoginRequiredMixin, CreateView):

    model = Account
    fields = ["name", "balance", "currency"]
    success_url = reverse_lazy("main:index")
    template_name = "main/create_account.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        try:
            self.object.save()
        except IntegrityError:
            messages.error(
                self.request,
                f"There is already a {self.object.name} account in your accounts.",
            )
            return self.form_invalid(form)
        return super().form_valid(form)


class EditAccountView(LoginRequiredMixin, UpdateView):

    model = Account
    fields = ["name", "balance", "currency"]
    template_name = "main/account_update.html"
    success_url = reverse_lazy("main:index")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def form_valid(self, form):
        try:
            self.object = form.save()
        except IntegrityError:
            messages.error(
                self.request,
                f"There is already a {self.object.name} account in your accounts.",
            )
            return self.form_invalid(form)
        return super().form_valid(form)


class DeleteAccountView(LoginRequiredMixin, DeleteView):

    model = Account
    success_url = reverse_lazy('main:index')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_active:
            raise Http404
        return obj

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.is_active = False
        self.object.save()
        return HttpResponseRedirect(success_url)


class LoansView(LoginRequiredMixin, ListView):
    pass


class CreateLoanView(LoginRequiredMixin, CreateView):

    login_url = reverse_lazy("main:login")
    model = Loan
    fields = ["name", "balance", "currency"]
    success_url = reverse_lazy("main:index")
    template_name = "main/create_loan.html"

    def form_valid(self, form):
        balance = form.cleaned_data["balance"]
        balance = -abs(balance)  # make balance negative
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.balance = balance
        try:
            self.object.save()
        except IntegrityError:
            messages.error(
                self.request,
                f"There is already {self.object.name} in your loans.",
            )
            return self.form_invalid(form)
        return super().form_valid(form)


class DeleteLoanView(LoginRequiredMixin, DeleteView):
    model = Loan
    success_url = reverse_lazy('main:index')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_active:
            raise Http404
        return obj

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.is_active = False
        self.object.save()
        return HttpResponseRedirect(success_url)


class LoanDetailView(LoginRequiredMixin, DetailView):
    pass


class EditLoanView(LoginRequiredMixin, UpdateView):

    model = Loan
    fields = ["name", "balance", "currency"]
    template_name = "main/loan_update.html"
    success_url = reverse_lazy("main:index")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def form_valid(self, form):
        form.instance.balance = -abs(form.cleaned_data["balance"])
        try:
            self.object = form.save()
        except IntegrityError:
            messages.error(
                self.request,
                f"There is already {self.object.name} in your loans.",
            )
            return self.form_invalid(form)
        return super().form_valid(form)


class PayLoanView(LoginRequiredMixin, FormView):

    form_class = PayLoanForm
    success_url = reverse_lazy('main:index')
    template_name = 'main/loan_pay.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs    

    def form_valid(self, form):
        data = form.cleaned_data
        account = data.get('account')
        loan = data.get('loan')
        amount = abs(data.get('amount'))
        date = data.get('date')
        category = Category.objects.get(user=self.request.user, name='Pay Loan')
        try:
            with transaction.atomic():
                if settings.TESTING_ATOMIC:
                    raise IntegrityError
                transaction_loan = Transaction(
                    account=account, 
                    name='Pay Loan', 
                    amount=amount, 
                    date=date, 
                    category=category, 
                    type='E'
                )
                transaction_loan.save()
                loan.balance += amount
                if loan.balance > 0:
                    loan.balance = 0
                loan.save()
                account.balance -= amount
                account.save()
        except IntegrityError:
            messages.error(self.request, 'Error during loan payment')
            context = self.get_context_data(form=form)
            return render(self.request, 'main/loan_pay.html', context)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        if 'form' not in kwargs:
            kwargs['form'] = self.form_class(user=self.request.user)
        account_data = get_account_data(self.request.user)
        loan_data = get_loan_data(self.request.user)
        context = {
            'account_data': account_data,
            'loan_data': loan_data,
        }
        context.update(kwargs)
        return context


class CategoriesView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        context = {
            "expense_categories": Category.objects.filter(
                user=user, type="E", is_protected=False
            ),
            "income_categories": Category.objects.filter(
                user=user, type="I", is_protected=False
            ),
        }
        return render(request, "main/categories.html", context)


class CreateExpenseCategory(UserPassesTestMixin, LoginRequiredMixin, View):
    
    def test_func(self):
        '''Tests if parent category belongs to user.'''
        id = self.request.POST.get("category_id", None)
        if id:
            return is_owner(self.request.user, Category, id)
        else:
            return True

    def post(self, request):
        user = request.user
        name = request.POST["category_name"]
        if name == '':
            messages.error(
                request, f"Category name can not be blank."
            )
            return HttpResponseRedirect(reverse("main:categories"))
        parent_id = request.POST.get("category_id", None)
        if parent_id:
            parent = get_object_or_404(Category, id=parent_id)
        else:
            if validate_main_category_uniqueness(name, user, type="E"):
                parent = None
            else:
                messages.error(
                    request, f"There is already a {name} category in main categories."
                )
                return HttpResponseRedirect(reverse("main:categories"))

        new_category = Category(name=name, parent=parent, user=user, type="E")
        try:
            new_category.save()
        except IntegrityError:
            messages.error(
                request,
                f"There is already a {name} category under {parent.name} category.",
            )
        return HttpResponseRedirect(reverse("main:categories"))


class CreateIncomeCategory(UserPassesTestMixin, LoginRequiredMixin, View):
    def test_func(self):
        '''Tests if parent category belongs to user.'''
        id = self.request.POST.get("category_id", None)
        if id:
            return is_owner(self.request.user, Category, id)
        else:
            return True

    def post(self, request):
        user = request.user
        name = request.POST["category_name"]
        if name == '':
            messages.error(
                request, f"Category name can not be blank."
            )
            return HttpResponseRedirect(reverse("main:categories"))
        parent_id = request.POST.get("category_id", None)
        if parent_id:
            parent = get_object_or_404(Category, id=parent_id)
        else:
            if validate_main_category_uniqueness(name, user, type="I"):
                parent = None
            else:
                messages.error(
                    request, f"There is already a {name} category in main categories."
                )
                return HttpResponseRedirect(reverse("main:categories"))

        new_category = Category(name=name, parent=parent, user=user, type="I")
        try:
            new_category.save()
        except IntegrityError:
            messages.error(
                request,
                f"There is already a {name} category under {parent.name} category.",
            )
        return HttpResponseRedirect(reverse("main:categories"))


class EditExpenseCategory(LoginRequiredMixin, View):
        
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def post(self, request):
        id = request.POST["category_id"]
        name = request.POST["category_name"]
        if name == '':
            messages.error(
                request, f"Category name can not be blank."
            )
            return HttpResponseRedirect(reverse("main:categories"))
        category_obj = get_object_or_404(self.get_queryset(), id=id)
        if category_obj.is_protected:
            raise Http404
        category_obj.name = name
        if Category.objects.filter(parent=category_obj.parent, name=name).exists():
            if category_obj.parent:
                messages.error(
                    request,
                    f"There is already a {name} category under {category_obj.parent.name} category.",
                )
            else:
                messages.error(
                    request, f"There is already a {name} category in main categories."
                )
        else:
            category_obj.save()
        return HttpResponseRedirect(reverse("main:categories"))


class EditIncomeCategory(LoginRequiredMixin, View):
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def post(self, request):
        id = request.POST["category_id"]
        name = request.POST["category_name"]
        if name == '':
            messages.error(
                request, f"Category name can not be blank."
            )
            return HttpResponseRedirect(reverse("main:categories"))
        category_obj = get_object_or_404(self.get_queryset(), id=id)
        if category_obj.is_protected:
            raise Http404
        category_obj.name = name
        if Category.objects.filter(parent=category_obj.parent, name=name).exists():
            if category_obj.parent:
                messages.error(
                    request,
                    f"There is already a {name} category under {category_obj.parent.name} category.",
                )
            else:
                messages.error(
                    request, f"There is already a {name} category in main categories."
                )
        else:
            category_obj.save()
        return HttpResponseRedirect(reverse("main:categories"))


class DeleteExpenseCategory(LoginRequiredMixin, DeleteView):        
    
    model = Category
    success_url = reverse_lazy('main:categories')
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def form_valid(self, form=None):
        if self.object.is_protected:
            raise Http404
        return super().form_valid(form)


class DeleteIncomeCategory(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('main:categories')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def form_valid(self, form=None):
        if self.object.is_protected:
            raise Http404
        return super().form_valid(form)
