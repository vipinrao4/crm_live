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
        'repeat_orders_count': 0,
    }
    return render(request, 'crm_core/admin_control.html', context)