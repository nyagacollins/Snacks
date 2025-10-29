from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('daily-sales/', views.daily_sales_report, name='daily_sales'),
    path('buyer/<int:buyer_id>/', views.buyer_report, name='buyer_report'),
    path('all-transactions/', views.all_transactions_report, name='all_transactions'),
]