from django.contrib import admin
from .models import Consumption, Transaction


@admin.register(Consumption)
class ConsumptionAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'mandazi_quantity', 'eggs_quantity', 'total_amount', 'payment_status', 'created_at')
    list_filter = ('payment_status', 'created_at')
    search_fields = ('buyer__username', 'buyer__email')
    readonly_fields = ('created_at',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'amount', 'phone_number', 'status', 'mpesa_receipt_number', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('buyer__username', 'phone_number', 'mpesa_receipt_number')
    readonly_fields = ('created_at', 'updated_at')