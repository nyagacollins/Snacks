from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from apps.accounts.decorators import seller_required
from apps.payments.utils import get_daily_sales_summary, get_buyer_analytics
from apps.payments.models import Transaction, Consumption

User = get_user_model()


@login_required
@seller_required
def daily_sales_report(request):
    # Get date from request or use today
    date_str = request.GET.get('date')
    if date_str:
        try:
            report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            report_date = timezone.now().date()
    else:
        report_date = timezone.now().date()
    
    # Get sales summary for the date
    sales_summary = get_daily_sales_summary(report_date)
    
    # Get recent dates for quick navigation
    recent_dates = []
    for i in range(7):
        date = timezone.now().date() - timedelta(days=i)
        recent_dates.append(date)
    
    context = {
        'sales_summary': sales_summary,
        'report_date': report_date,
        'recent_dates': recent_dates
    }
    
    return render(request, 'reports/daily_sales.html', context)


@login_required
@seller_required
def buyer_report(request, buyer_id):
    buyer = get_object_or_404(
        User, 
        id=buyer_id, 
        created_by=request.user, 
        role='BUYER'
    )
    
    # Get analytics for different periods
    analytics_30 = get_buyer_analytics(buyer, 30)
    analytics_7 = get_buyer_analytics(buyer, 7)
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        buyer=buyer,
        status='SUCCESS'
    )[:10]
    
    # Get recent consumptions
    recent_consumptions = Consumption.objects.filter(
        buyer=buyer,
        payment_status='PAID'
    )[:10]
    
    context = {
        'buyer': buyer,
        'analytics_30': analytics_30,
        'analytics_7': analytics_7,
        'recent_transactions': recent_transactions,
        'recent_consumptions': recent_consumptions
    }
    
    return render(request, 'reports/buyer_report.html', context)


@login_required
@seller_required
def all_transactions_report(request):
    # Get all transactions for buyers created by this seller
    transactions = Transaction.objects.filter(
        buyer__created_by=request.user
    ).select_related('buyer', 'consumption')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        transactions = transactions.filter(status=status_filter)
    
    # Filter by date range if provided
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            transactions = transactions.filter(created_at__date__gte=from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            transactions = transactions.filter(created_at__date__lte=to_date)
        except ValueError:
            pass
    
    # Pagination could be added here if needed
    transactions = transactions[:100]  # Limit to 100 for performance
    
    context = {
        'transactions': transactions,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to
    }
    
    return render(request, 'reports/all_transactions.html', context)