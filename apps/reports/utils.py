from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from apps.payments.models import Transaction, Consumption


def generate_monthly_report(year, month, seller):
    """Generate comprehensive monthly report for a seller"""
    # Get first and last day of the month
    first_day = datetime(year, month, 1).date()
    if month == 12:
        last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    # Get transactions for the month
    transactions = Transaction.objects.filter(
        buyer__created_by=seller,
        created_at__date__range=[first_day, last_day],
        status='SUCCESS'
    )
    
    # Calculate totals
    totals = transactions.aggregate(
        total_revenue=Sum('amount'),
        total_transactions=Count('id'),
        average_transaction=Avg('amount')
    )
    
    # Get consumption data
    consumptions = Consumption.objects.filter(
        buyer__created_by=seller,
        created_at__date__range=[first_day, last_day],
        payment_status='PAID'
    )
    
    consumption_totals = consumptions.aggregate(
        total_mandazi=Sum('mandazi_quantity'),
        total_eggs=Sum('eggs_quantity')
    )
    
    # Get daily breakdown
    daily_sales = []
    current_date = first_day
    while current_date <= last_day:
        day_transactions = transactions.filter(created_at__date=current_date)
        day_total = day_transactions.aggregate(total=Sum('amount'))['total'] or 0
        daily_sales.append({
            'date': current_date,
            'total': day_total,
            'transaction_count': day_transactions.count()
        })
        current_date += timedelta(days=1)
    
    return {
        'month': month,
        'year': year,
        'first_day': first_day,
        'last_day': last_day,
        'total_revenue': totals['total_revenue'] or 0,
        'total_transactions': totals['total_transactions'] or 0,
        'average_transaction': totals['average_transaction'] or 0,
        'total_mandazi_sold': consumption_totals['total_mandazi'] or 0,
        'total_eggs_sold': consumption_totals['total_eggs'] or 0,
        'daily_sales': daily_sales
    }


def get_top_buyers(seller, days=30):
    """Get top buyers by spending in the last N days"""
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get buyers with their total spending
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    buyers = User.objects.filter(
        created_by=seller,
        role='BUYER',
        transactions__created_at__date__range=[start_date, end_date],
        transactions__status='SUCCESS'
    ).annotate(
        total_spent=Sum('transactions__amount'),
        transaction_count=Count('transactions')
    ).order_by('-total_spent')[:10]
    
    return buyers