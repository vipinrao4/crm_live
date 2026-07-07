import os
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Order  
from datetime import datetime

@login_required
def dashboard_view(request):
    user = request.user
    raw_orders = Order.objects.filter(employee=user).order_by('-date')
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        raw_orders = raw_orders.filter(date__range=[start_date, end_date])

    # Backend standard formatting: Date ko string bana kar bhej rahe hain taaki HTML filter crash na ho
    orders = []
    for order in raw_orders:
        formatted_date = order.date.strftime("%d-%m-%Y") if order.date else ""
        orders.append({
            'formatted_date': formatted_date,
            'customer_name': order.customer_name,
            'phone_1': order.phone_1,
            'district': order.district,
            'state': order.state,
            'product_1_name': getattr(order, 'product_1_name', ''),
            'product_1_count': getattr(order, 'product_1_count', 0),
            'product_2_name': getattr(order, 'product_2_name', ''),
            'product_2_count': getattr(order, 'product_2_count', 0),
            'product_3_name': getattr(order, 'product_3_name', ''),
            'product_3_count': getattr(order, 'product_3_count', 0),
            'grand_total': order.grand_total,
            'status': order.status,
        })

    context = {
        'orders': orders,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    try:
        return render(request, 'dashboard.html', context)
    except Exception:
        return render(request, 'crm_core/dashboard.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
        
    try:
        return render(request, 'login.html', {'form': form})
    except Exception:
        return render(request, 'crm_core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')