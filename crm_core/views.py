from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.apps import apps

@login_required
def dashboard(request):
    orders_list = []
    
    # Database se data safe nikalne ka tarika taaki crash na ho
    try:
        OrderModel = apps.get_model('crm_core', 'Order')
        orders_list = OrderModel.objects.all().order_by('-id')
    except Exception:
        pass

    context = {
        'orders': orders_list,
        'total_orders': len(orders_list) if orders_list else 1,
        'total_products_sold': 1,
        'repeat_orders_count': 0,
        'performance_data': [],
    }
    return render(request, 'admin_control.html', context)