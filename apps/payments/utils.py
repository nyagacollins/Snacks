from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Transaction, Consumption


def get_daily_sales_summary(date=None):
    """Get sales summary for a specific date"""
    if date is None:
        date = timezone.now().date()
    
    # Get successful transactions for the date
    transactions = Transaction.objects.filter(
        created_at__date=date,
        status='SUCCESS'
    )
    
    total_sales = transactions.aggregate(
        total_amount=Sum('amount'),
        total_transactions=Count('id')
    )
    
    # Get consumption details
    consumptions = Consumption.objects.filter(
        created_at__date=date,
        payment_status='PAID'
    )
    
    consumption_summary = consumptions.aggregate(
        total_mandazi=Sum('mandazi_quantity'),
        total_eggs=Sum('eggs_quantity')
    )
    
    return {
        'date': date,
        'total_amount': total_sales['total_amount'] or 0,
        'total_transactions': total_sales['total_transactions'] or 0,
        'total_mandazi_sold': consumption_summary['total_mandazi'] or 0,
        'total_eggs_sold': consumption_summary['total_eggs'] or 0,
        'transactions': transactions
    }


def get_buyer_analytics(buyer, days=30):
    """Get analytics for a specific buyer"""
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    consumptions = Consumption.objects.filter(
        buyer=buyer,
        created_at__date__range=[start_date, end_date],
        payment_status='PAID'
    )
    
    analytics = consumptions.aggregate(
        total_spent=Sum('total_amount'),
        total_mandazi=Sum('mandazi_quantity'),
        total_eggs=Sum('eggs_quantity'),
        total_purchases=Count('id')
    )
    
    return {
        'buyer': buyer,
        'period_days': days,
        'total_spent': analytics['total_spent'] or 0,
        'total_mandazi_consumed': analytics['total_mandazi'] or 0,
        'total_eggs_consumed': analytics['total_eggs'] or 0,
        'total_purchases': analytics['total_purchases'] or 0,
        'average_per_purchase': (analytics['total_spent'] or 0) / max(analytics['total_purchases'] or 1, 1)
    }