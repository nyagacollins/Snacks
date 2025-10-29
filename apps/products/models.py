from django.db import models


class Product(models.Model):
    PRODUCT_CHOICES = [
        ('MANDAZI', 'Mandazi'),
        ('EGGS', 'Eggs'),
    ]
    
    name = models.CharField(max_length=20, choices=PRODUCT_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_name_display()} - KSh {self.price}"
    
    class Meta:
        ordering = ['name']