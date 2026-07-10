from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order
from django.db.models import Q
from django.http import JsonResponse
import re

@login_required
def emp_dashboard_view(request):
    # AJAX Search for Phone
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.GET.get('action') == 'search_phone':
        q = request.GET.get('phone', '')
        o = Order.objects.filter(Q(phone__icontains=q) | Q(customer_phone__icontains=q)).first()
        return JsonResponse({'status': 'success', 'name': o.customer_name, 'address': o.address, 'total': o.total} if o else {'status': 'not_found'})
    
    # POST Save Logic
    if request.method == 'POST':
        phone1 = request.POST.get('phone1', '')
        # Detect Repeat
        is_repeat = Order.objects.filter(Q(phone__icontains=phone1) | Q(customer_phone__icontains=phone1)).exists()
        # Save logic (apna purana save logic yahan aayega)
        
    return render(request, 'crm_core/dashboard.html', {'orders': Order.objects.all()})

@login_required
def dashboard(request):
    # Admin Panel logic (yahan apka admin logic rahega)
    return render(request, 'crm_core/admin_control.html', {})

@login_required
def admin_update_status(request, order_id):
    if request.method == 'POST':
        o = Order.objects.get(id=order_id)
        o.status = 'Pending' if (request.POST.get('status') == 'Generated' and o.status == 'Generated') else request.POST.get('status')
        o.save()
    return redirect('dashboard')