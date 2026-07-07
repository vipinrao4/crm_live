import os
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from .models import Order  
from datetime import datetime

@login_required
def dashboard_view(request):
    user = request.user
    
    # -----------------------------------------------------------------
    # ROUTE 1: MASTER ADMIN CONTROL (Agar user superuser ya staff hai)
    # -----------------------------------------------------------------
    if user.is_staff or user.is_superuser:
        raw_orders = Order.objects.all().order_by('-date')
        
        # Filters parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        search_phone = request.GET.get('search_phone')
        
        if start_date and end_date:
            raw_orders = raw_orders.filter(date__range=[start_date, end_date])
            
        if search_phone:
            raw_orders = raw_orders.filter(Q(phone_1__icontains=search_phone) | Q(phone_2__icontains=search_phone))
            
        # Top Stats Cards Calculation
        total_orders_count = raw_orders.count()
        
        total_products_sold = 0
        repeat_orders_count = 0
        
        for o in raw_orders:
            # Har order ke products ka count jodna
            total_products_sold += (getattr(o, 'product_1_count', 0) or 0) + (getattr(o, 'product_2_count', 0) or 0) + (getattr(o, 'product_3_count', 0) or 0)
            if getattr(o, 'is_repeat', False):
                repeat_orders_count += 1
                
        # Employee Performance Summary Calculation
        employees = User.objects.filter(is_staff=False)
        emp_summary = []
        for emp in employees:
            emp_orders = raw_orders.filter(employee=emp)
            emp_p_count = 0
            emp_repeat_count = 0
            for eo in emp_orders:
                emp_p_count += (getattr(eo, 'product_1_count', 0) or 0) + (getattr(eo, 'product_2_count', 0) or 0) + (getattr(eo, 'product_3_count', 0) or 0)
                if getattr(eo, 'is_repeat', False):
                    emp_repeat_count += 1
            
            emp_summary.append({
                'username': emp.username,
                'new_orders_units': emp_orders.count() - emp_repeat_count,
                'repeat_orders_units': emp_repeat_count,
                'total_products_sold': emp_p_count,
                'ads_spent': 0.0, # Placeholder custom display
                'avg_cost': 0.0,
            })
            
        # Master Log Mapping
        master_orders_log = []
        for o in raw_orders:
            items_desc = f"{o.product_1_name or ''} (x{o.product_1_count or 0})"
            if o.product_2_name:
                items_desc += f", {o.product_2_name} (x{o.product_2_count or 0})"
            if o.product_3_name:
                items_desc += f", {o.product_3_name} (x{o.product_3_count or 0})"
                
            master_orders_log.append({
                'date': o.date.strftime("%d-%m-%Y") if o.date else "",
                'emp': o.employee.username if o.employee else "System",
                'customer_info': f"{o.customer_name} | {o.phone_1}",
                'full_address': f"{o.address or ''}, {o.tehsil or ''}, {o.district or ''}, {o.state or ''} - {o.pincode or ''}",
                'items_summary': items_desc,
                'grand_total': o.grand_total or 0,
                'status': o.status or "Pending",
            })
            
        context = {
            'total_orders_count': total_orders_count,
            'total_products_sold': total_products_sold,
            'repeat_orders_count': repeat_orders_count,
            'emp_summary': emp_summary,
            'master_orders_log': master_orders_log,
            'start_date': start_date,
            'end_date': end_date,
            'search_phone': search_phone or '',
        }
        return render(request, 'admin_control.html', context)

    # -----------------------------------------------------------------
    # ROUTE 2: EMPLOYEE PORTAL (Agar normal user login hai)
    # -----------------------------------------------------------------
    if request.method == 'POST':
        # New Order submission matching screenshot inputs
        customer_name = request.POST.get('name')
        phone_1 = request.POST.get('phone_1')
        phone_2 = request.POST.get('phone_2')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
        tehsil = request.POST.get('tehsil')
        post_office = request.POST.get('post')
        district = request.POST.get('district')
        state = request.POST.get('state')
        
        p1_name = request.POST.get('product_1')
        p1_count = int(request.POST.get('product_1_count', 1) or 1)
        p1_price = float(request.POST.get('product_1_price', 0) or 0)
        
        p2_name = request.POST.get('product_2')
        p2_count = int(request.POST.get('product_2_count', 0) or 0)
        p2_price = float(request.POST.get('product_2_price', 0) or 0)
        
        p3_name = request.POST.get('product_3')
        p3_count = int(request.POST.get('product_3_count', 0) or 0)
        p3_price = float(request.POST.get('product_3_price', 0) or 0)
        
        # Automatic Grand Total calculation on backend
        grand_total = (p1_count * p1_price) + (p2_count * p2_price) + (p3_count * p3_price)
        
        # Check if customer is a repeat user
        is_customer_repeat = Order.objects.filter(phone_1=phone_1).exists()

        Order.objects.create(
            employee=user,
            customer_name=customer_name,
            phone_1=phone_1,
            phone_2=phone_2,
            address=address,
            pincode=pincode,
            tehsil=tehsil,
            post_office=post_office,
            district=district,
            state=state,
            product_1_name=p1_name,
            product_1_count=p1_count,
            product_2_name=p2_name,
            product_2_count=p2_count,
            product_3_name=p3_name,
            product_3_count=p3_count,
            grand_total=grand_total,
            is_repeat=is_customer_repeat,
            date=datetime.now().date(),
            status='Pending'
        )
        return redirect('dashboard')

    # Fetch Employee's personal orders log for synchronization view
    raw_emp_orders = Order.objects.filter(employee=user).order_by('-date')
    emp_orders_list = []
    for o in raw_emp_orders:
        emp_orders_list.append({
            'date': o.date.strftime("%d-%m-%Y") if o.date else "",
            'customer_name': o.customer_name,
            'phone_1': o.phone_1,
            'items': f"{o.product_1_name or ''} ({o.product_1_count or 0})",
            'grand_total': o.grand_total or 0,
            'status': o.status or "Pending"
        })

    return render(request, 'dashboard.html', {'emp_orders_list': emp_orders_list})

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
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')