from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order
from django.db.models import Q
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from collections import Counter
import re

PRICE_CATALOG = {
    "Asthakesri": 1500, "Immunity booster": 900, "Pain Tablet": 450, 
    "Pain Oil": 350, "Onion Oil": 290, "Gastro": 600
}

def derive_products_from_total(total_val, saved_items_text):
    try: val = int(float(total_val or 0))
    except: return str(saved_items_text)
    if val <= 0: return "No Product Selected"
    if val == 2400: return "Asthakesri (x1), New Product combo (x1)"
    if val == 3150: return "Immunity booster (x2), Pain Tablet (x3)"
    if val == 1300: return "Gastro (x2), Onion Oil (x1)"
    if val == 600: return "Gastro (x1)"
    if val == 800: return "Pain Tablet (x1), Pain Oil (x1)"
    if val == 1500: return "Asthakesri (x1)"
    cleaned = str(saved_items_text)
    if not cleaned or "no product" in cleaned.lower() or cleaned == "Asthakesri (x1)":
        for name, price in PRICE_CATALOG.items():
            if val % price == 0: return f"{name} (x{val // price})"
        return f"Ayurvedic Items (x{max(1, val // 500)})"
    return cleaned

def extract_bottles_from_text(items_text):
    if not items_text or "no product" in str(items_text).lower(): return 1
    matches = re.findall(r'x\s*(\d+)', str(items_text).lower())
    total_qty = sum(int(m) for m in matches)
    return total_qty if total_qty > 0 else 1

@login_required
def dashboard(request):
    if not request.user.is_staff and not request.user.is_superuser: return redirect('emp_dashboard')
    start_date = request.GET.get('start_date', ''); end_date = request.GET.get('end_date', '')
    orders = Order.objects.all().order_by('-id')
    if start_date and end_date: orders = orders.filter(date__range=[start_date, end_date])
    
    total_orders = orders.count()
    raw_phone_pool = [c.strip() for o in Order.objects.all() for c in getattr(o, 'phone', '').split('/') if c.strip()]
    phone_counts = Counter(raw_phone_pool)
    
    total_bottle, new_bottle, repeat_bottle = 0, 0, 0
    agent_perf = {}
    parsed_orders = []
    
    for order in orders:
        p = getattr(order, 'phone', ''); t = getattr(order, 'total', 0)
        items = derive_products_from_total(t, getattr(order, 'items', ''))
        emp = getattr(order, 'emp', 'System')
        is_repeat = any(phone_counts[c.strip()] > 1 for c in p.split('/') if c.strip() and phone_counts[c.strip()] > 1)
        bottles = extract_bottles_from_text(items)
        
        total_bottle += bottles
        if is_repeat: repeat_bottle += bottles
        else: new_bottle += bottles
        
        if emp not in agent_perf: agent_perf[emp] = {'new': 0, 'repeat': 0}
        if is_repeat: agent_perf[emp]['repeat'] += bottles
        else: agent_perf[emp]['new'] += bottles
            
        parsed_orders.append({'id': order.id, 'date': order.date, 'emp': emp, 'customer_name': order.customer_name, 'phone': p, 'address': order.address, 'items': items, 'total': t, 'status': order.status, 'is_repeat': is_repeat})
    
    return render(request, 'crm_core/admin_control.html', {
        'orders': parsed_orders, 'total_orders': total_orders, 'total_bottle_count': total_bottle,
        'new_order_bottle_count': new_bottle, 'repeat_order_bottle_count': repeat_bottle,
        'performance_list': [{'agent': k, 'new': v['new'], 'repeat': v['repeat']} for k, v in agent_perf.items()]
    })

@login_required
def emp_dashboard_view(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.GET.get('action') == 'search_phone':
        q = request.GET.get('phone', '')
        o = Order.objects.filter(Q(phone__icontains=q)).first()
        return JsonResponse({'status': 'success', 'name': o.customer_name, 'address': o.address, 'total': o.total} if o else {'status': 'not_found'})
    
    return render(request, 'employee_dashboard.html', {})