from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager


class User(AbstractUser):
    ROLE_CHOICES = [
        ('SELLER', 'Seller'),
        ('BUYER', 'Buyer'),
    ]
    
    phone_number = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='BUYER')
    created_by = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='created_buyers'
    )
    
    objects = UserManager()
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def is_seller(self):
        return self.role == 'SELLER'
    
    def is_buyer(self):
        return self.role == 'BUYER'