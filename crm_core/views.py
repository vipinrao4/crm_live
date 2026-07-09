from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def dashboard(request):
    # Dynamic Routing: Agar user employee hai (staff nahi hai), toh use employee page par bhejo
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('emp_dashboard')

    # Agar admin hai, toh admin panel ka data load karo
    try:
        orders = Order.objects.all().order_by('-id')
        total_orders = orders.count()
    except Exception:
        orders = []
        total_orders = 0

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'total_products_sold': total_orders,
        'repeat_orders_count': 0,
    }
    return render(request, 'crm_core/admin_control.html', context)


@login_required
def emp_dashboard_view(request):
    context = {
        'username': request.user.username
    }
    # Dynamic path handling employee template ke liye
    try:
        return render(request, 'crm_core/emp_dashboard.html', context)
    except Exception:
        return render(request, 'emp_dashboard.html', context)