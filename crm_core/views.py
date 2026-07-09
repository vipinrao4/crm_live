from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def dashboard(request):
    # Strict Security Check: Agar user admin/staff nahi hai, toh use logout karke login page par phek do
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('/accounts/login/?error=unauthorized')

    # Agar admin hai, toh hi niche wala asli data load hoga
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
        'repeat_ordefrom django.shortcuts import render, redirect
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
    # Yeh aapka original employee page render karega jahan wo orders punch karte hain
    context = {
        'username': request.user.username
    }
    # Jo bhi aapke original employee HTML file ka naam tha (jaise emp_dashboard.html ya index.html), wo yahan likhiye
    try:
        return render(request, 'crm_core/emp_dashboard.html', context)
    except Exception:
        # Fallback agar file naam thoda alag ho
        return render(request, 'emp_dashboard.html', context)s_count': 0,
    }
    return render(request, 'crm_core/admin_control.html', context)