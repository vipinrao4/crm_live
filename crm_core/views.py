from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def dashboard(request):
    orders = Order.objects.all().order_by('-id')
    
    # Ekdum pehle wale original counters
    total_orders = orders.count()
    total_products_sold = total_orders  # Jo aapka original fallback chal raha tha
    repeat_orders_count = 0

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'total_products_sold': total_products_sold,
        'repeat_orders_count': repeat_orders_count,
    }
    return render(request, 'admin_control.html', context)