from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order  # Agar aapke model ka naam kuch aur hai toh change kar lena
from datetime import datetime

@login_required
def dashboard(request):
    user = request.user
    
    # Base query: Sirf login employee ke orders dikhayein
    orders = Order.objects.filter(employee=user).order_by('-created_at') # date field ka naam check kar lena
    
    # Date filtering ka logic
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        # Django query filter for date range
        orders = orders.filter(created_at__date__range=[start_date, end_date])

    context = {
        'orders': orders,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'dashboard.html', context)