from datetime import datetime, date
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import (
    CreateView,
    UpdateView,
    ListView,
    DetailView,
    DeleteView,
    FormView,
    TemplateView,
    MonthArchiveView,
    WeekArchiveView,
    YearArchiveView,
    DayArchiveView,
    ArchiveIndexView,
)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.http import (
    HttpResponseRedirect,
    HttpResponse,
    JsonResponse,
    Http404,
)
from django.urls import reverse, reverse_lazy
from .models import (
    Account,
    Transfer,
    User,
    Transaction,
    Category,
    Loan,
    Currency,
    UserPreferences,
)
from .forms import (
    ExpenseInputForm,
    IncomeInputForm,
    TransferForm,
    PayLoanForm,
    LoanDetailPaymentForm,
    SetupForm,
    EditTransactionForm,
)
from .view_mixins import (
    InsOutsDateArchiveMixin,
    CategoryDateArchiveMixin,
    SubcategoryDateArchiveMixin,
    AccountDetailDateArchiveMixin,
    TransfersDateArchiveMixin,
    TransactionsDateArchiveMixin
)
from .utils import (
    create_transaction,
    edit_asset_balance,
    get_latest_transactions,
    get_latest_transfers,
    get_account_data,
    get_account_balance_data,
    get_loan_data,
    get_loan_balance_data,
    get_subcategory_stats,
    handle_transaction_delete,
    validate_main_category_uniqueness,
    get_dates,
    get_stats,
    is_owner,
    get_category_stats,
    get_multi_currency_category_stats,
    get_paginated_qs,
    get_comparison_stats,
    get_subcategory_stats,
    get_loan_progress,
    get_payment_stats,
    get_worth_stats,
    get_currency_details,
    get_users_grand_total,
    withdraw_asset_balance,
    create_transfer,
    handle_loan_payment,
    handle_asset_delete,
    handle_transfer_delete,
    handle_transfer_edit,
    get_ins_outs_report,
    get_report_total,
    get_multi_currency_category_detail_stats,
    get_multi_currency_category_json_stats,
)
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.conf import settings


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("main:main"))
    return render(request, "main/index.html")


@login_required(login_url=reverse_lazy("main:login"))
def main(request):
    transfer_form = TransferForm(user=request.user)
    expense_form = ExpenseInputForm(request.user)
    income_form = IncomeInputForm(request.user)

    if request.method == "POST":
        # transfer form operations
        if request.POST.get("submit-transfer"):
            form = TransferForm(request.POST, user=request.user)
            if form.is_valid():
                data = form.cleaned_data
                try:
                    create_transfer(data, request.user)
                except IntegrityError:
                    messages.error(request, "Error during transfer")
                return HttpResponseRedirect(reverse("main:main"))
            else:
                transfer_form = form

        # expense form operations
        if request.POST.get("submit-expense"):
            form = ExpenseInputForm(request.user, request.POST)
            if form.is_valid():
                create_transaction(form.cleaned_data)
                return HttpResponseRedirect(reverse("main:main"))
            else:
                expense_form = form
        #  income form operations
        if request.POST.get("submit-income"):
            form = IncomeInputForm(request.user, request.POST)
            if form.is_valid():
                create_transaction(form.cleaned_data)
                return HttpResponseRedirect(reverse("main:main"))
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
        "account_balance_data": get_account_balance_data(request.user),
        "show_account": True,
    }
    return render(request, "main/main.html", context)


@login_required
def transaction_name_autocomplete(request):
    name_query = request.GET.get("name", None)
    type = request.GET.get("type", None)
    name_list = []
    if name_query:
        user = request.user
        accounts_list = Account.objects.filter(
            user=user, is_active=True
        ).values_list("id", flat=True)
        incomes = Transaction.objects.filter(
            object_id__in=accounts_list, name__icontains=name_query, type=type
        )
        for income in incomes:
            name_list.append(income.name)
    return JsonResponse({"status": 200, "data": name_list})


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("main:main"))
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
            return HttpResponseRedirect(reverse("main:main"))
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
        return HttpResponseRedirect(reverse("main:setup"))


class SetupView(LoginRequiredMixin, FormView):
    form_class = SetupForm
    success_url = reverse_lazy("main:main")
    template_name = "main/setup.html"

    def form_valid(self, form):
        primary_currency = form.cleaned_data["currency"]
        user_preferences = self.request.user.user_preferences
        user_preferences.primary_currency = primary_currency
        user_preferences.save()
        return super().form_valid(form)


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
        return HttpResponse(
            '<p class="text-muted mx-2" id="username_check_text"></p>'
        )


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return HttpResponseRedirect(reverse("main:index"))


class AccountsView(LoginRequiredMixin, ListView):
    model = Account
    template_name = "main/accounts.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(user=self.request.user, is_active=True)
            .select_related("currency")
        )


class CreateAccountView(LoginRequiredMixin, CreateView):

    model = Account
    fields = ["name", "balance", "currency"]
    success_url = reverse_lazy("main:main")
    template_name = "main/create_account.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.initial = self.object.balance
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
    success_url = reverse_lazy("main:main")

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
    success_url = reverse_lazy("main:main")

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(user=self.request.user, is_active=True)
        )

    def form_valid(self, form):
        handle_asset_delete(self.object)
        self.object.is_active = False
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class LoansView(LoginRequiredMixin, ListView):
    pass


class CreateLoanView(LoginRequiredMixin, CreateView):

    login_url = reverse_lazy("main:login")
    model = Loan
    fields = ["name", "balance", "currency"]
    success_url = reverse_lazy("main:main")
    template_name = "main/create_loan.html"

    def form_valid(self, form):
        balance = form.cleaned_data["balance"]
        balance = -abs(balance)  # make balance negative
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.balance = balance
        self.object.initial = balance
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
    success_url = reverse_lazy("main:main")

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(user=self.request.user, is_active=True)
        )

    def form_valid(self, form):
        handle_asset_delete(self.object)
        self.object.is_active = False
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class LoanDetailView(LoginRequiredMixin, DetailView):
    model = Loan
    template_name: str = "main/loan_detail.html"

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        loan = self.get_object()
        form = LoanDetailPaymentForm(user=self.request.user, loan=loan)
        transactions = (
            Transaction.objects.filter(
                content_type__model="loan",
                object_id=loan.id,
            )
            .order_by("-date", "-created")
            .prefetch_related("content_object__currency")
        )
        page_obj = get_paginated_qs(
            transactions, self.request, settings.DEFAULT_PAGINATION_QTY
        )
        extra_context = {
            "progress": get_loan_progress(self.object),
            "transactions": page_obj,
            "payment_stats": get_payment_stats(self.object),
            "form": form,
        }
        return super().get_context_data(**extra_context)


class LoanDetailAjaxView(LoginRequiredMixin, DetailView):

    model = Loan
    template_name = "main/loan_detail_pack.html"

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_active:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        loan = self.get_object()
        qs = Transaction.objects.filter(
            content_type__model="loan", object_id=loan.id
        ).order_by("-date", "-created")
        context = {
            "transactions": get_paginated_qs(
                qs, self.request, settings.DEFAULT_PAGINATION_QTY
            ),
        }
        return super().get_context_data(**context)


class EditLoanView(LoginRequiredMixin, UpdateView):

    model = Loan
    fields = ["name", "balance", "currency"]
    template_name = "main/loan_update.html"
    success_url = reverse_lazy("main:main")

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
    success_url = reverse_lazy("main:main")
    template_name = "main/loan_pay.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def form_valid(self, form):
        try:
            handle_loan_payment(form)
        except IntegrityError:
            messages.error(self.request, "Error during loan payment")
            context = self.get_context_data(form=form)
            return render(self.request, "main/loan_pay.html", context)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        if "form" not in kwargs:
            kwargs["form"] = self.form_class(user=self.request.user)
        account_data = get_account_data(self.request.user)
        loan_data = get_loan_data(self.request.user)
        loan_balance_data = get_loan_balance_data(self.request.user)
        account_balance_data = get_account_balance_data(self.request.user)
        context = {
            "account_data": account_data,
            "loan_data": loan_data,
            "loan_balance_data": loan_balance_data,
            "account_balance_data": account_balance_data
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
        """Tests if parent category belongs to user."""
        id = self.request.POST.get("category_id", None)
        if id:
            return is_owner(self.request.user, Category, id)
        else:
            return True

    def post(self, request):
        user = request.user
        name = request.POST["category_name"]
        if name == "":
            messages.error(request, f"Category name can not be blank.")
            return HttpResponseRedirect(reverse("main:categories"))
        parent_id = request.POST.get("category_id", None)
        if parent_id:
            parent = get_object_or_404(Category, id=parent_id)
        else:
            if validate_main_category_uniqueness(name, user, type="E"):
                parent = None
            else:
                messages.error(
                    request,
                    f"There is already a {name} category in main categories.",
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
        """Tests if parent category belongs to user."""
        id = self.request.POST.get("category_id", None)
        if id:
            return is_owner(self.request.user, Category, id)
        else:
            return True

    def post(self, request):
        user = request.user
        name = request.POST["category_name"]
        if name == "":
            messages.error(request, f"Category name can not be blank.")
            return HttpResponseRedirect(reverse("main:categories"))
        parent_id = request.POST.get("category_id", None)
        if parent_id:
            parent = get_object_or_404(Category, id=parent_id)
        else:
            if validate_main_category_uniqueness(name, user, type="I"):
                parent = None
            else:
                messages.error(
                    request,
                    f"There is already a {name} category in main categories.",
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
        if name == "":
            messages.error(request, f"Category name can not be blank.")
            return HttpResponseRedirect(reverse("main:categories"))
        category_obj = get_object_or_404(self.get_queryset(), id=id)
        if category_obj.is_protected:
            raise Http404
        category_obj.name = name
        if Category.objects.filter(
            parent=category_obj.parent, name=name
        ).exists():
            if category_obj.parent:
                messages.error(
                    request,
                    f"There is already a {name} category under {category_obj.parent.name} category.",
                )
            else:
                messages.error(
                    request,
                    f"There is already a {name} category in main categories.",
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
        if name == "":
            messages.error(request, f"Category name can not be blank.")
            return HttpResponseRedirect(reverse("main:categories"))
        category_obj = get_object_or_404(self.get_queryset(), id=id)
        if category_obj.is_protected:
            raise Http404
        category_obj.name = name
        if Category.objects.filter(
            parent=category_obj.parent, name=name
        ).exists():
            if category_obj.parent:
                messages.error(
                    request,
                    f"There is already a {name} category under {category_obj.parent.name} category.",
                )
            else:
                messages.error(
                    request,
                    f"There is already a {name} category in main categories.",
                )
        else:
            category_obj.save()
        return HttpResponseRedirect(reverse("main:categories"))


class DeleteExpenseCategory(LoginRequiredMixin, DeleteView):

    model = Category
    success_url = reverse_lazy("main:categories")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def form_valid(self, form=None):
        if self.object.is_protected:
            raise Http404
        return super().form_valid(form)


class DeleteIncomeCategory(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy("main:categories")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def form_valid(self, form=None):
        if self.object.is_protected:
            raise Http404
        return super().form_valid(form)


class WorthView(LoginRequiredMixin, TemplateView):

    template_name = "main/worth.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        extra_context = {
            "stats": get_worth_stats(self.request.user),
            "currency_details": get_currency_details(self.request.user),
        }
        extra_context["grand_total"] = get_users_grand_total(
            user=self.request.user, data=extra_context["currency_details"]
        )
        kwargs.update(extra_context)
        return kwargs


class TransactionsView(TransactionsDateArchiveMixin, ArchiveIndexView):
    template_name = "main/transactions.html"
    

class TransactionsAllArchiveView(TransactionsDateArchiveMixin, ArchiveIndexView):
    pass


class TransactionsYearArchiveView(TransactionsDateArchiveMixin, YearArchiveView):
    pass


class TransactionsMonthArchiveView(TransactionsDateArchiveMixin, MonthArchiveView):
    pass


class TransactionsWeekArchiveView(TransactionsDateArchiveMixin, WeekArchiveView):
    pass


class TransactionsDayArchiveView(TransactionsDateArchiveMixin, DayArchiveView):
    pass


class EditTransactionView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = EditTransactionForm
    success_url = reverse_lazy("main:main")
    template_name = "main/transaction_edit.html"

    def get_queryset(self):
        user_accounts_list = Account.objects.filter(
            user=self.request.user
        ).values_list("id", flat=True)
        return super().get_queryset().filter(object_id__in=user_accounts_list)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def form_valid(self, form):
        try:
            with transaction.atomic():
                withdraw_asset_balance(
                    self.get_object()
                )  # get initial object from get_object method
                self.object = form.save()
                edit_asset_balance(self.object)
        except IntegrityError:
            messages.error(self.request, "Error during transaction update")
            context = self.get_context_data(form=form)
            return render(self.request, self.template_name, context)
        return HttpResponseRedirect(self.get_success_url())


class DeleteTransactionView(LoginRequiredMixin, DeleteView):
    model = Transaction
    success_url = reverse_lazy("main:main")

    def get_queryset(self):
        queryset = super().get_queryset()
        accounts_list = Account.objects.filter(
            user=self.request.user
        ).values_list("id", flat=True)
        return queryset.filter(object_id__in=accounts_list)

    def form_valid(self, form):
        try:
            handle_transaction_delete(self.object)
        except IntegrityError:
            messages.error(self.request, "Error during transaction update")
        finally:
            return HttpResponseRedirect(self.get_success_url())


class TransfersView(TransfersDateArchiveMixin, ArchiveIndexView):
    template_name = "main/transfers.html"


class TransfersAllArchiveView(TransfersDateArchiveMixin, ArchiveIndexView):
    pass


class TransfersYearArchiveView(TransfersDateArchiveMixin, YearArchiveView):
    pass


class TransfersMonthArchiveView(TransfersDateArchiveMixin, MonthArchiveView):
    pass


class TransfersWeekArchiveView(TransfersDateArchiveMixin, WeekArchiveView):
    pass


class TransfersDayArchiveView(TransfersDateArchiveMixin, DayArchiveView):
    pass


class DeleteTransferView(LoginRequiredMixin, DeleteView):
    model = Transfer
    success_url = reverse_lazy("main:transfers")

    def get(self, request, *args, **kwargs):
        raise Http404()

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def form_valid(self, form):
        if not self.object.is_editable:
            messages.error(self.request, "This transfer has deleted account(s) and is not editable.")
            return HttpResponseRedirect(self.get_success_url())
        try:
            handle_transfer_delete(self.object)
        except IntegrityError:
            messages.error(self.request, "Error during deleting transfer")
        finally:
            return HttpResponseRedirect(self.get_success_url())


class EditTransferView(LoginRequiredMixin, UpdateView):
    model = Transfer
    success_url = reverse_lazy("main:transfers")
    form_class = TransferForm
    template_name = "main/transfer_edit.html"

    def get(self, request, *args, **kwargs):
        transfer_obj = self.get_object()
        if not transfer_obj.is_editable:
            messages.error(request, "This transfer has deleted account(s) and is not editable.")
            return HttpResponseRedirect(reverse('main:transfers'))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs.update(
            {
                "account_data": get_account_data(self.request.user),
            }
        )
        return kwargs

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        data = {
            "from_account": self.object.from_transaction.content_object,
            "from_amount": self.object.from_transaction.amount,
            "to_account": self.object.to_transaction.content_object,
            "to_amount": self.object.to_transaction.amount,
            "date": self.object.date,
            "user": self.request.user,
        }
        kwargs.update({"user": self.request.user})
        kwargs["data"] = kwargs.get("data", data)
        del kwargs["instance"]
        return kwargs

    def form_valid(self, form):
        try:
            handle_transfer_edit(self.object, form.cleaned_data)
        except IntegrityError:
            messages.error(self.request, "Error during editing transfer")
            return self.render_to_response(self.get_context_data(form=form))
        return HttpResponseRedirect(reverse("main:main"))


class InsOutsView(InsOutsDateArchiveMixin, ArchiveIndexView):
    template_name = "main/ins_outs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"date": date.today()})
        return context


class InsOutsAllArchiveView(InsOutsDateArchiveMixin, ArchiveIndexView):
    pass


class InsOutsYearArchiveView(InsOutsDateArchiveMixin, YearArchiveView):
    pass


class InsOutsMonthArchiveView(InsOutsDateArchiveMixin, MonthArchiveView):
    pass


class InsOutsWeekArchiveView(InsOutsDateArchiveMixin, WeekArchiveView):
    pass


class InsOutsDayArchiveView(InsOutsDateArchiveMixin, DayArchiveView):
    pass


class CategoryDetailView(CategoryDateArchiveMixin, ArchiveIndexView):
    template_name = "main/category_detail.html"


class CategoryAllArchiveView(CategoryDateArchiveMixin, ArchiveIndexView):
    pass


class CategoryYearArchiveView(CategoryDateArchiveMixin, YearArchiveView):
    pass


class CategoryMonthArchiveView(CategoryDateArchiveMixin, MonthArchiveView):
    pass


class CategoryWeekArchiveView(CategoryDateArchiveMixin, WeekArchiveView):
    pass


class CategoryDayArchiveView(CategoryDateArchiveMixin, DayArchiveView):
    pass


class SubcategoryStatsAllArchiveView(
    SubcategoryDateArchiveMixin, ArchiveIndexView
):
    pass


class SubcategoryStatsYearArchiveView(
    SubcategoryDateArchiveMixin,
    UserPassesTestMixin,
    LoginRequiredMixin,
    YearArchiveView,
):
    pass


class SubcategoryStatsMonthArchiveView(
    SubcategoryDateArchiveMixin,
    UserPassesTestMixin,
    LoginRequiredMixin,
    MonthArchiveView,
):
    pass


class SubcategoryStatsWeekArchiveView(
    SubcategoryDateArchiveMixin,
    UserPassesTestMixin,
    LoginRequiredMixin,
    WeekArchiveView,
):
    pass


class SubcategoryStatsDayArchiveView(
    SubcategoryDateArchiveMixin,
    UserPassesTestMixin,
    LoginRequiredMixin,
    DayArchiveView,
):
    pass


class AccountDetailView(AccountDetailDateArchiveMixin, ArchiveIndexView):
    template_name = "main/account_detail.html"


class AccountDetailAllArchiveView(
    AccountDetailDateArchiveMixin, ArchiveIndexView
):
    pass


class AccountDetailYearArchiveView(
    AccountDetailDateArchiveMixin, YearArchiveView
):
    pass


class AccountDetailMonthArchiveView(
    AccountDetailDateArchiveMixin, MonthArchiveView
):
    pass


class AccountDetailWeekArchiveView(
    AccountDetailDateArchiveMixin, WeekArchiveView
):
    pass


class AccountDetailDayArchiveView(
    AccountDetailDateArchiveMixin, DayArchiveView
):
    pass


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "main/profile.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        currencies = Currency.objects.all()
        user_currency = self.request.user.primary_currency
        kwargs.update({"currencies": currencies, "user_currency": user_currency})
        return kwargs

class UpdateProfileView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        currency_id = self.request.POST["currency"]
        new_currency = get_object_or_404(Currency, pk=currency_id)
        preferences = UserPreferences.objects.get(user=self.request.user)
        preferences.primary_currency = new_currency
        preferences.save()
        return HttpResponseRedirect(reverse('main:profile'))