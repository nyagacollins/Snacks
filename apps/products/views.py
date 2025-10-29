from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import seller_required, buyer_required
from .models import Product
from .forms import ProductPriceForm, SnackSelectionForm


@login_required
@seller_required
def manage_products(request):
    products = Product.objects.all()
    return render(request, 'products/manage_products.html', {'products': products})


@login_required
@seller_required
def update_product_price(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductPriceForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'{product.get_name_display()} price updated successfully!')
            return redirect('products:manage_products')
    else:
        form = ProductPriceForm(instance=product)
    
    return render(request, 'products/update_price.html', {'form': form, 'product': product})


@login_required
@buyer_required
def select_snacks(request):
    try:
        mandazi = Product.objects.get(name='MANDAZI')
        eggs = Product.objects.get(name='EGGS')
    except Product.DoesNotExist:
        messages.error(request, 'Products not found. Please contact the seller.')
        return redirect('accounts:dashboard')
    
    total_amount = 0
    
    if request.method == 'POST':
        form = SnackSelectionForm(request.POST)
        if form.is_valid():
            mandazi_qty = form.cleaned_data['mandazi_quantity']
            eggs_qty = form.cleaned_data['eggs_quantity']
            
            if mandazi_qty == 0 and eggs_qty == 0:
                messages.warning(request, 'Please select at least one item.')
            else:
                total_amount = (mandazi_qty * mandazi.price) + (eggs_qty * eggs.price)
                
                # Store in session for payment processing
                request.session['consumption_data'] = {
                    'mandazi_quantity': mandazi_qty,
                    'eggs_quantity': eggs_qty,
                    'mandazi_price': float(mandazi.price),
                    'eggs_price': float(eggs.price),
                    'total_amount': float(total_amount)
                }
                
                return redirect('payments:payment_form')
    else:
        form = SnackSelectionForm()
    
    context = {
        'form': form,
        'mandazi': mandazi,
        'eggs': eggs,
        'total_amount': total_amount
    }
    
    return render(request, 'products/select_snacks.html', context)