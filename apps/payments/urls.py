from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('payment-form/', views.payment_form, name='payment_form'),
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
    path('success/<int:transaction_id>/', views.payment_success, name='payment_success'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),
    path('consumption-history/', views.consumption_history, name='consumption_history'),
    path('all-transactions/', views.all_transactions, name='all_transactions'),
    path('mpesa-status/', views.mpesa_status, name='mpesa_status'),
    path('check-status/<int:transaction_id>/', views.check_payment_status, name='check_payment_status'),
    path('test-stk/', views.test_stk_push, name='test_stk_push'),
    path('test-callback/', views.test_callback, name='test_callback'),
    path('simulate-callback/<int:transaction_id>/', views.simulate_callback, name='simulate_callback'),
    path('callback-monitor/', views.callback_monitor, name='callback_monitor'),
    path('manual-confirm/<int:transaction_id>/', views.manual_confirm_payment, name='manual_confirm_payment'),
]