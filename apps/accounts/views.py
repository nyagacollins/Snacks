from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from .forms import CustomLoginForm, BuyerRegistrationForm, PhoneNumberUpdateForm
from .decorators import seller_required, buyer_required

User = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('accounts:dashboard')
    else:
        form = CustomLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def dashboard(request):
    if request.user.is_seller():
        return render(request, 'accounts/seller_dashboard.html')
    else:
        return render(request, 'accounts/buyer_dashboard.html')


@login_required
@seller_required
def register_buyer(request):
    if request.method == 'POST':
        form = BuyerRegistrationForm(request.POST)
        if form.is_valid():
            buyer = form.save(commit=False)
            buyer.created_by = request.user
            buyer.save()
            messages.success(request, f'Buyer {buyer.username} registered successfully!')
            return redirect('accounts:manage_buyers')
    else:
        form = BuyerRegistrationForm()
    
    return render(request, 'accounts/register_buyer.html', {'form': form})


@login_required
@seller_required
def manage_buyers(request):
    buyers = User.objects.filter(created_by=request.user, role='BUYER')
    return render(request, 'accounts/manage_buyers.html', {'buyers': buyers})


@login_required
@seller_required
def toggle_buyer_status(request, buyer_id):
    buyer = get_object_or_404(User, id=buyer_id, created_by=request.user, role='BUYER')
    buyer.is_active = not buyer.is_active
    buyer.save()
    
    status = 'activated' if buyer.is_active else 'deactivated'
    messages.success(request, f'Buyer {buyer.username} has been {status}.')
    return redirect('accounts:manage_buyers')


@login_required
@buyer_required
def update_phone(request):
    if request.method == 'POST':
        form = PhoneNumberUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Phone number updated successfully!')
            return redirect('accounts:dashboard')
    else:
        form = PhoneNumberUpdateForm(instance=request.user)
    
    return render(request, 'accounts/update_phone.html', {'form': form})