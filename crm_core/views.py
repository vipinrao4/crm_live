from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order  # Aapka original Order model

@login_required
def dashboard(request):
    # Ekdum original query bina kisi badlav ke
    orders = Order.objects.all().order_by('-id')
    
    # Aapke original counters aur variables
    total_orders = orders.count()
    total_products_sold = sum(order.product_count for order in orders if hasattr(order, 'product_count')) or total_orders
    repeat_orders_count = sum(1 for order in orders if hasattr(order, 'is_repeat') and order.is_repeat)

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'total_products_sold': total_products_sold,
        'repeat_orders_count': repeat_orders_count,
    }
    return render(request, 'admin_control.html', context)