from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available', 'created_at', 'updated_at')
    list_filter = ('is_available', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')