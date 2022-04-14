from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from requests import request
from .models import Account, User, CostCategory, IncomeCategory
from .forms import AccountForm
from django.db import IntegrityError

# Create your views here.
def index(request):
    context = {}
    return render(request, 'main/index.html', context)


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
                return HttpResponseRedirect(reverse('main:wallet'))
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
        return HttpResponseRedirect(reverse('main:wallet'))


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


def wallet(request):

    context = {
        'categories': CostCategory.objects.filter(user=request.user)
    }
    return render(request, 'main/wallet.html', context)

class AccountsView(ListView):
    pass

class CreateAccountView(CreateView):
    model = Account
    fields = ['name', 'balance', 'currency']
    success_url = reverse_lazy('main:wallet')
    template_name = 'main/create_account.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)

class UpdateAccount(UpdateView):
    pass