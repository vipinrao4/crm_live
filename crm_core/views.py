from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order
from django.db.models import Q
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from collections import Counter
import re

# Bottle count helper
def extract_bottles_from_text(items_text):
    if not items_text or "no product" in str(items_text).lower(): return 1
    matches = re.findall(r'x\s*(\d+)', str(items_text).lower())
    total = sum(int(m) for m in matches)
    return total if total > 0 else 1

@login_required
def dashboard(request):
    if not request.user.is_staff and not request.user.is_superuser: return redirect('emp_dashboard')
    
    start_date = request.GET.get('start_date', ''); end_date = request.GET.get('end_date', '')
    orders = Order.objects.all().order_by('-id')
    if start_date and end_date: orders = orders.filter(date__range=[start_date, end_date])
    
    # Repeat/Bottle logic
    raw_phones = [c.strip() for o in Order.objects.all() for c in getattr(o, 'phone', '').split('/') if c.strip()]
    counts = Counter(raw_phones)
    
    t_bottle, n_bottle, r_bottle = 0, 0, 0
    perf = {}
    parsed = []
    
    for o in orders:
        p = getattr(o, 'phone', ''); t = getattr(o, 'total', 0); i = getattr(o, 'items', 'Asthakesri (x1)')
        e = getattr(o, 'emp', 'System')
        is_r = any(counts[c.strip()] > 1 for c in p.split('/') if c.strip() and counts[c.strip()] > 1)
        b = extract_bottles_from_text(i)
        
        t_bottle += b
        if is_r: r_bottle += b
        else: n_bottle += b
        
        if e not in perf: perf[e] = {'n': 0, 'r': 0}
        if is_r: perf[e]['r'] += b
        else: perf[e]['n'] += b
            
        parsed.append({'id': o.id, 'emp': e, 'customer_name': o.customer_name, 'phone': p, 'address': o.address, 'items': i, 'total': t, 'status': o.status, 'is_repeat': is_r})
    
    return render(request, 'crm_core/admin_control.html', {
        'orders': parsed, 'total_bottle_count': t_bottle, 'new_order_bottle_count': n_bottle,
        'repeat_order_bottle_count': r_bottle, 'performance_list': [{'agent': k, 'n': v['n'], 'r': v['r']} for k, v in perf.items()]
    })

@login_required
def admin_update_status(request, order_id):
    if request.method == 'POST':
        o = Order.objects.get(id=order_id)
        o.status = 'Pending' if (request.POST.get('status') == 'Generated' and o.status == 'Generated') else request.POST.get('status')
        o.save()
    return redirect('dashboard')

@login_required
def emp_dashboard_view(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.GET.get('action') == 'search_phone':
        q = request.GET.get('phone', '')
        o = Order.objects.filter(phone__icontains=q).first()
        return JsonResponse({'status': 'success', 'name': o.customer_name, 'address': o.address, 'total': o.total} if o else {'status': 'not_found'})
    
    return render(request, 'employee_dashboard.html', {'orders': Order.objects.all()})