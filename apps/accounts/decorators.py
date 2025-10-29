from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def seller_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_seller():
            messages.error(request, 'Access denied. Seller privileges required.')
            return redirect('accounts:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def buyer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_buyer():
            messages.error(request, 'Access denied. Buyer privileges required.')
            return redirect('accounts:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view