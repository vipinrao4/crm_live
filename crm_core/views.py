from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .models import Order
from django.db.models import Q
import re

def custom_login(request):
    if request.method == 'POST':
        # Simple login logic
        return redirect('dashboard')
    return render(request, 'login.html') # Ye aapke root template folder mein honi chahiye

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_admin, login_url='/accounts/login/')
def dashboard(request):
    return render(request, 'crm_core/admin_control.html', {})

@login_required
def emp_dashboard_view(request):
    return render(request, 'dashboard.html', {'orders': Order.objects.all()})

@login_required
def admin_update_status(request, order_id):
    if request.method == 'POST':
        o = Order.objects.get(id=order_id)
        o.status = request.POST.get('status')
        o.save()
    return redirect('dashboard')