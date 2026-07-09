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
    
    # Pehle direct try karega, nahi toh background automatic settings handle karegi
    try:
        return render(request, 'admin_control.html', context)
    except Exception:
        return render(request, 'crm_core/admin_control.html', context)