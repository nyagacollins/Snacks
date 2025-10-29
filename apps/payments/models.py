from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Consumption(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    ]
    
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consumptions')
    mandazi_quantity = models.PositiveIntegerField(default=0)
    eggs_quantity = models.PositiveIntegerField(default=0)
    mandazi_price = models.DecimalField(max_digits=10, decimal_places=2)
    eggs_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.buyer.username} - KSh {self.total_amount} ({self.payment_status})"
    
    class Meta:
        ordering = ['-created_at']


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]
    
    consumption = models.OneToOneField(Consumption, on_delete=models.CASCADE, related_name='transaction')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)
    mpesa_transaction_id = models.CharField(max_length=50, blank=True, null=True)
    checkout_request_id = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Transaction {self.id} - {self.buyer.username} - KSh {self.amount}"
    
    class Meta:
        ordering = ['-created_at']