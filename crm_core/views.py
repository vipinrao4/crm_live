from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Order
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from collections import Counter
import re

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def derive_products_from_total(total_val, saved_items_text):
    try: val = int(float(total_val or 0))
    except: return str(saved_items_text)
    if val <= 0: return "No Product Selected"
    # Mapping for Price Totals
    catalog = {2400: "Asthakesri (x1), Combo (x1)", 3150: "Immunity booster (x2), Pain Tablet (x3)", 
               1300: "Gastro (x2), Onion Oil (x1)", 600: "Gastro (x1)", 
               800: "Pain Tablet (x1), Pain Oil (x1)", 1500: "Asthakesri (x1)"}
    if val in catalog: return catalog[val]
    return str(saved_items_text)

def extract_bottles_from_text(items_text):
    if not items_text or "no product" in str(items_text).lower(): return 1
    matches = re.findall(r'x\s*(\d+)', str(items_text).lower())
    total = sum(int(m) for m in matches)
    return total if total > 0 else 1

@user_passes_test(is_admin, login_url='/accounts/login/')
def dashboard(request):
    start = request.GET.get('start_date', ''); end = request.GET.get('end_date', '')
    orders = Order.objects.all().order_by('-id')
    if start and end: orders = orders.filter(date__range=[start, end])
    
    raw_phones = [c.strip() for o in Order.objects.all() for c in getattr(o, 'phone', '').split('/') if c.strip()]
    counts = Counter(raw_phones)
    
    t_b, n_b, r_b = 0, 0, 0
    perf = {}
    parsed = []
    
    for o in orders:
        p = getattr(o, 'phone', ''); t = getattr(o, 'total', 0)
        i = derive_products_from_total(t, getattr(o, 'items', 'Asthakesri (x1)'))
        e = getattr(o, 'emp', 'System')
        is_r = any(counts[c.strip()] > 1 for c in p.split('/') if c.strip() and counts[c.strip()] > 1)
        b = extract_bottles_from_text(i)
        
        t_b += b
        if is_r: r_b += b
        else: n_b += b
        
        if e not in perf: perf[e] = {'n': 0, 'r': 0}
        if is_r: perf[e]['r'] += b
        else: perf[e]['n'] += b
            
        parsed.append({'id': o.id, 'date': o.date, 'emp': e, 'customer_name': o.customer_name, 'phone': p, 'address': o.address, 'items': i, 'total': t, 'status': o.status})
    
    return render(request, 'crm_core/admin_control.html', {
        'orders': parsed, 'total_bottle_count': t_b, 'new_order_bottle_count': n_b,
        'repeat_order_bottle_count': r_b, 'performance_list': [{'agent': k, 'n': v['n'], 'r': v['r']} for k, v in perf.items()]
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
        o = Order.objects.filter(Q(phone__icontains=q)).first()
        return JsonResponse({'status': 'success', 'name': o.customer_name, 'address': o.address, 'total': o.total} if o else {'status': 'not_found'})
    return render(request, 'crm_core/dashboard.html', {'orders': Order.objects.all().order_by('-id')})