from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('manage/', views.manage_products, name='manage_products'),
    path('update-price/<int:product_id>/', views.update_product_price, name='update_product_price'),
    path('select-snacks/', views.select_snacks, name='select_snacks'),
]