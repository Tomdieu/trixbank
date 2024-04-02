from django.shortcuts import render,redirect
from django.views.generic.base import TemplateView,View
from .forms import LoginForm,AuthenticationForm,UserCreationForm,DepositForm,WithdrawForm,TransferForm,UserChangeForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import login,logout,authenticate
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
import re
from django.contrib.auth.decorators import login_required

from core.templatetags.custom_filters import xaf_currency,format_account_number
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Account,Transaction,Deposit,Transfer,Withdraw,TransactionStatus,TransactionType,Notification

# Create your views here.

class LandingPageView(TemplateView):
    
    template_name = "landing.html"
    
class AboutPageView(TemplateView):
    
    template_name = "about.html"
    
def loginView(request):
    template_name = "core/login.html"
    context = {}
    
    if request.method == "GET" and request.user.is_authenticated:
        # If it's a GET request and the user is authenticated, redirect to the dashboard
        return redirect(reverse("dashboard"))

            

    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            # Process the valid form data
            # For example, authenticate the user and redirect
            
            username = request.POST.get('username',None)
            password = request.POST.get('password',None)
            
            user = authenticate(request=request,username=username,password=password)
            
            if user is not None:
                
                login(request,user)
                
                url_name = "dashboard"
                
                messages.success(request,"Login Successfull",extra_tags="bg-green-100 border-green-500 text-green-700")
                
                return redirect(reverse(url_name))
            
            
            else:
                context['form'] = form
                # send an error for password of username incorrect
                messages.error(request, "Incorrect username or password", extra_tags="bg-red-100 border-red-500 text-red-700")
            
        else:
            # If the form is not valid, return the form with errors
            context['form'] = form
    else:
        # If it's a GET request, just display the form
        context['form'] = LoginForm()

    return render(request, template_name, context)

@login_required(login_url='login')
def logoutView(request):
    
    logout(request)
    
    return redirect(reverse("landing"))
    

def registerView(request):
    
    template_name = "core/register.html"
    context = {}
    
    if request.method == "GET" and request.user.is_authenticated:
        # If it's a GET request and the user is authenticated, redirect to the dashboard
        return redirect(reverse("dashboard"))

    
    if request.method == "POST":
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            # Process the valid form data
            # For example, authenticate the user and redirect
            
            form.save()
            
            username = request.POST.get('username',None)
            password = request.POST.get('password',None)
            
            user = authenticate(request=request,username=username,password=password)
            
            if user is not None:
                
                login(request,user)
                
                messages.success(request,"Welcome to Trixbank")
                
                return redirect(reverse("dashboard"))
            
            else:
                
                return redirect(reverse("login"))
        else:
            # If the form is not valid, return the form with errors
            context['form'] = form
    
    else:
        # If it's a GET request, just display the form
        context['form'] = UserCreationForm()

    return render(request, template_name, context)
    
    
@login_required(login_url="login")
def dashboardView(request):
    
    template_name = "core/dashboard.html"
    
    context = {}
    
    if request.method == "GET":
        
        user_account = request.user.account
    
        context['transactions'] = Transaction.objects.filter(Q(source_account=user_account))[:5]
    
    return render(request,template_name,context)

@login_required(login_url='login')
def depositView(request):
    
    template_name = "core/dashboard/deposit.html"
    
    context = {}
    
    if request.method == "POST":
        
        form = DepositForm(data=request.POST)
        
        if form.is_valid():
            
            amount = request.POST.get('amount')
            
            user_account = request.user.account
            
            deposit = Deposit.objects.create(source_account=user_account,amount=amount)
            
            if deposit.status == TransactionStatus.SUCCESS:
                
                messages.success(request,f"You Deposit {xaf_currency(amount)} Successfully.",extra_tags="bg-green-100 border-green-500 text-green-700")
            
            else:
                
                messages.error(request,f"Something went wrong and you couldn't deposit {xaf_currency(amount)}.", extra_tags="bg-red-100 border-red-500 text-red-700")
            
        
        else:
            
            context['form'] = form
        
    else:
    
        context['form'] = DepositForm()
    
    return render(request,template_name,context)
    
@login_required(login_url='login')
def withdrawView(request):
    
    template_name = "core/dashboard/withdraw.html"
    
    context = {}
    
    if request.method == "POST":
        
        form = WithdrawForm(data=request.POST)
        
        if form.is_valid():
            
            amount = request.POST.get('amount')
            
            user_account = request.user.account
            
            widthdraw = Withdraw.objects.create(source_account=user_account,amount=amount)
            
            if widthdraw.status == TransactionStatus.SUCCESS:
            
                messages.success(request,f"You Withdraw {xaf_currency(amount)} Successfully",extra_tags="bg-green-100 border-green-500 text-green-700")
            
            else:
                
                messages.error(request,f"You couldn't widthdraw {xaf_currency(amount)} from your account.",extra_tags="bg-red-100 border-red-500 text-red-700")
            
        
        else:
            
            context['form'] = form
        
    else:
    
        context['form'] = WithdrawForm()
    
    return render(request,template_name,context)

@login_required(login_url='login')
def transferView(request):
    
    template_name = "core/dashboard/transfer.html"
    context = {}
    
    if request.method == "POST":
        
        form = TransferForm(data=request.POST,initial={'current_user_account_number': request.user.account.account_number})
        
        if form.is_valid():
            print("Form Valid")
            amount = request.POST.get('amount')
            user_account = request.user.account
            current_user_account_number = form.cleaned_data['current_user_account_number']
            reciepient_account_number = re.sub(r'\s+', '', request.POST.get('reciepient_account_number', ""))
            destination_account = None
            
            destination_account_ = Account.objects.filter(account_number=reciepient_account_number)
            
            if not destination_account_.exists():
                messages.error(request,f"The account number {format_account_number(reciepient_account_number)} does not exist in TrixBank")
            else:
                destination_account = destination_account_.first()

                with transaction.atomic():
                    try:
                        transfer = Transfer.objects.create(source_account=user_account, destination_account=destination_account, amount=amount)
                        if transfer.status == TransactionStatus.SUCCESS:
                            messages.success(request,f"You Transfer {xaf_currency(amount)} Successfully to {destination_account.user}.",extra_tags="bg-green-100 border-green-500 text-green-700")
                        else:
                            messages.error(request,f"Sorry you could not transfer {xaf_currency(amount)}.",extra_tags="bg-red-100 border-red-500 text-red-700")
                    except Exception as e:
                        messages.error(request, f"An error occurred while processing the transfer: {str(e)}",extra_tags="bg-red-100 border-red-500 text-red-700")
                        # No need to manually rollback, Django handles it automatically

        else:
            context['form'] = form
    else:
        context['form'] = TransferForm(initial={'current_user_account_number': request.user.account.account_number})
    
    return render(request, template_name, context)


@login_required(login_url="login")
def historyView(request):
    
    template_name = "core/dashboard/history.html"
    
    context = {}
    user_account = request.user.account
    
    queryset = Transaction.objects.filter(Q(source_account=user_account) | Q(destination_account=user_account))
    
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page',1)
    
    try:
        transactions = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        transactions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        transactions = paginator.page(paginator.num_pages)
       
    context['transactions'] = transactions
    
    print(transactions)
    
    return render(request,template_name,context)


@login_required(login_url='login')
def transfer_partial(request):
    
    template_name = "core/partials/transfer.html"
    
    context = {}
    
    user_account = request.user.account
    
    context['transactions'] = Transfer.objects.filter(Q(source_account=user_account) | Q(destination_account=user_account))
    
    return render(request,template_name,context)

@login_required(login_url='login')
def withdraw_partial(request):
    
    template_name = "core/partials/deposit_withdrawl.html"
    
    context = {}
    
    user_account = request.user.account
    
    context['transactions'] = Withdraw.objects.filter(Q(source_account=user_account) | Q(destination_account=user_account))
    
    return render(request,template_name,context)
    
    
@login_required(login_url='login')
def deposit_partial(request):
    
    template_name = "core/partials/deposit_withdrawl.html"
    
    context = {}
    
    user_account = request.user.account
    
    context['transactions'] = Deposit.objects.filter(Q(source_account=user_account) | Q(destination_account=user_account))
    
    return render(request,template_name,context)

@login_required(login_url='login')
def profileView(request):
    template_name = "core/dashboard/profile.html"
    context = {}
    
    
    return render(request, template_name, context)


@login_required(login_url='login')
def updateProfileView(request):
    template_name = "core/dashboard/profile/update.html"
    context = {}
    
    user_account = request.user
    
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user_account)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            
            return redirect(reverse('profile'))
        else:
            # If form is not valid, pass it back to the template with errors
            context['form'] = form
    else:
        # For GET requests, initialize the form with user data
        user_data = {'username': user_account.username, 'email': user_account.email}  # Add more fields as needed
        form = UserChangeForm(data=user_data)
        context['form'] = form
    
    return render(request, template_name, context)

@login_required(login_url='login')
def changePasswordView(request):
    template_name = "core/dashboard/profile/change_password.html"
    context = {}
    
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to update the session
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')  # Redirect to the profile page or any other page
    else:
        form = PasswordChangeForm(user=request.user)
    
    context['form'] = form
    
    return render(request, template_name, context)

@login_required(login_url='login')
def notificationView(request):
    
    template_name = "core/dashboard/notifications.html"
    
    context = {}
    
    user = request.user
    
    context['notifications'] = Notification.objects.filter(user=user)
    
    return render(request,template_name,context)
