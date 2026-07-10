from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.http import JsonResponse
from .models import Order
from django.db.models import Q
from datetime import datetime

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def custom_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('/')
        return redirect('/employee/dashboard/')

    error_msg = None
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        user = authenticate(request, username=u, password=p)
        if user is not None:
            django_login(request, user)
            if user.is_staff or user.is_superuser:
                return redirect('/')
            else:
                return redirect('/employee/dashboard/')
        else:
            error_msg = "Invalid Username or Password!"
            
    return render(request, 'crm_core/login.html', {'error': error_msg})

# NAYA LOGOUT FUNCTION
def custom_logout(request):
    django_logout(request)
    return redirect('/accounts/login/')

@login_required(login_url='/accounts/login/')
def emp_dashboard_view(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.GET.get('action') == 'search_phone':
        q = request.GET.get('phone', '')
        o = Order.objects.filter(Q(phone1=q) | Q(phone2=q)).order_by('-id').first()
        if o:
            return JsonResponse({'status': 'success', 'data': {
                'name': o.customer_name, 'phone1': o.phone1, 'phone2': o.phone2,
                'address': o.address, 'pincode': o.pincode, 'post_office': o.post_office,
                'tehsil': o.tehsil, 'district': o.district, 'state': o.state,
                'last_date': o.date.strftime('%Y-%m-%d')
            }})
        return JsonResponse({'status': 'not_found'})

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        phone1 = request.POST.get('phone1')
        phone2 = request.POST.get('phone2')
        
        is_rep = Order.objects.filter(Q(phone1=phone1) | Q(phone2=phone1)).exclude(id=order_id if order_id else None).exists()
        
        if order_id:
            o = Order.objects.get(id=order_id, emp=request.user.username)
        else:
            o = Order()
            o.emp = request.user.username
            
        o.is_repeat = is_rep
        o.customer_name = request.POST.get('customer_name')
        o.phone1 = phone1
        o.phone2 = phone2
        o.address = request.POST.get('address')
        o.pincode = request.POST.get('pincode')
        o.post_office = request.POST.get('post_office')
        o.tehsil = request.POST.get('tehsil')
        o.district = request.POST.get('district')
        o.state = request.POST.get('state')
        o.items_summary = request.POST.get('items_summary')
        o.total_bottles = int(request.POST.get('total_bottles', 0))
        o.grand_total = int(request.POST.get('grand_total', 0))
        o.save()
        return redirect('emp_dashboard')

    today_str = datetime.today().strftime('%Y-%m-%d')
    start_date = request.GET.get('start_date', today_str)
    end_date = request.GET.get('end_date', today_str)
    
    my_orders = Order.objects.filter(emp=request.user.username).order_by('-id')
    if start_date and end_date:
        my_orders = my_orders.filter(date__date__gte=start_date, date__date__lte=end_date)
    
    ctx = {
        'orders': my_orders, 'start_date': start_date, 'end_date': end_date,
        'new_ord_count': my_orders.filter(is_repeat=False).count(),
        'rep_ord_count': my_orders.filter(is_repeat=True).count(),
        'new_bot_count': sum(o.total_bottles for o in my_orders if not o.is_repeat),
        'rep_bot_count': sum(o.total_bottles for o in my_orders if o.is_repeat),
    }
    return render(request, 'crm_core/dashboard.html', ctx)

@user_passes_test(is_admin, login_url='/accounts/login/')
def dashboard(request):
    today_str = datetime.today().strftime('%Y-%m-%d')
    start_date = request.GET.get('start_date', today_str)
    end_date = request.GET.get('end_date', today_str)
    search_q = request.GET.get('search', '')

    orders = Order.objects.all().order_by('-id')
    
    if search_q:
        orders = orders.filter(Q(phone1__icontains=search_q) | Q(phone2__icontains=search_q))
    elif start_date and end_date:
        orders = orders.filter(date__date__gte=start_date, date__date__lte=end_date)

    agent_data = {}
    for o in orders:
        if o.emp not in agent_data:
            agent_data[o.emp] = {'new_b': 0, 'rep_b': 0}
        if o.is_repeat: agent_data[o.emp]['rep_b'] += o.total_bottles
        else: agent_data[o.emp]['new_b'] += o.total_bottles

    ctx = {
        'orders': orders, 'start_date': start_date, 'end_date': end_date, 'search_q': search_q,
        'tot_new_ord': orders.filter(is_repeat=False).count(),
        'tot_rep_ord': orders.filter(is_repeat=True).count(),
        'tot_new_bot': sum(o.total_bottles for o in orders if not o.is_repeat),
        'tot_rep_bot': sum(o.total_bottles for o in orders if o.is_repeat),
        'agents': [{'name': k, **v} for k, v in agent_data.items()]
    }
    return render(request, 'crm_core/admin_control.html', ctx)

@login_required
def admin_update_status(request, order_id):
    o = Order.objects.get(id=order_id)
    new_status = request.GET.get('status')
    if o.status == 'Generated' and new_status == 'Generated':
        o.status = 'Pending'
    else:
        o.status = new_status
    o.save()
    return redirect('dashboard')