from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order  
from datetime import datetime

@login_required
def dashboard_view(request):
    user = request.user
    
    # Base query: Sirf login employee ke orders dikhayein
    orders = Order.objects.filter(employee=user).order_by('-created_at')
    
    # Date filtering ka logic
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        orders = orders.filter(created_at__date__range=[start_date, end_date])

    context = {
        'orders': orders,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'dashboard.html', context)