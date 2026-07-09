from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def dashboard(request):
    try:
        orders = Order.objects.all().order_by('-id')
        total_orders = orders.count()
    except Exception:
        orders = []
        total_orders = 1

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'total_products_sold': total_orders,
        'repeat_orders_count': 0,
    }
    
    # Isko explicit app template path de rahe hain taaki Django turant dhoodh le!
    return render(request, 'crm_core/admin_control.html', context)