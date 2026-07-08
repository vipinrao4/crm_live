import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from .models import Order  
from datetime import datetime

@login_required
def dashboard(request):
    user = request.user
    
    # AJAX Status Update Handler (Generated/Cancel buttons ke liye)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        try:
            order_obj = Order.objects.get(id=order_id)
            order_obj.status = new_status
            order_obj.save()
            return JsonResponse({'status': 'success'})
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'})

    # -----------------------------------------------------------------
    # ROUTE 1: MASTER ADMIN CONTROL (Admin ya Superuser View)
    # -----------------------------------------------------------------
    if user.is_staff or user.is_superuser:
        raw_orders = Order.objects.all().order_by('-date')
        
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        search_phone = request.GET.get('search_phone')
        
        if start_date and end_date:
            raw_orders = raw_orders.filter(date__range=[start_date, end_date])
            
        if search_phone:
            raw_orders = raw_orders.filter(Q(phone_1__icontains=search_phone) | Q(phone_2__icontains=search_phone))
            
        total_orders_count = raw_orders.count()
        total_products_sold = 0
        repeat_orders_count = 0
        
        for o in raw_orders:
            total_products_sold += (getattr(o, 'product_1_count', 0) or 0) + (getattr(o, 'product_2_count', 0) or 0) + (getattr(o, 'product_3_count', 0) or 0)
            if getattr(o, 'is_repeat', False):
                repeat_orders_count += 1
                
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
            
            new_orders_units = emp_orders.count() - emp_repeat_count
            
            emp_summary.append({
                'username': emp.username,
                'new_orders_units': new_orders_units if new_orders_units > 0 else 0,
                'repeat_orders_units': emp_repeat_count,
                'total_products_sold': emp_p_count,
            })
            
        master_orders_log = []
        for o in raw_orders:
            items_list = []
            if o.product_1_name and (o.product_1_count or 0) > 0:
                items_list.append(f"* {o.product_1_name} (x{o.product_1_count})")
            if o.product_2_name and (o.product_2_count or 0) > 0:
                items_list.append(f"* {o.product_2_name} (x{o.product_2_count})")
            if o.product_3_name and (o.product_3_count or 0) > 0:
                items_list.append(f"* {o.product_3_name} (x{o.product_3_count})")
            
            items_desc = ", ".join([i.replace("* ", "") for i in items_list])
            whatsapp_items = "\n".join(items_list)
            
            # WhatsApp Format Mapping
            wa_text = (
                f"Customer Name: {o.customer_name}\n"
                f"Phone: {o.phone_1 or ''}{', ' + o.phone_2 if o.phone_2 else ''}\n"
                f"Address: {o.address or ''}\n"
                f"Post: {o.post_office or ''}\n"
                f"Tehsil: {o.tehsil or ''}\n"
                f"District: {o.district or ''}\n"
                f"State: {o.state or ''}\n"
                f"Pincode: {o.pincode or ''}\n"
                f"Items Summary:\n{whatsapp_items}\n\n"
                f"Grand Total Price: Rs. {int(o.grand_total or 0)}\n"
                f"-------------------------------------------\n"
                f"Order Booked By: {o.employee.username if o.employee else 'Admin'}"
            )
            
            master_orders_log.append({
                'id': o.id,
                'date': o.date.strftime("%d-%m-%Y") if o.date else "",
                'emp': o.employee.username if o.employee else "System",
                'customer_info': f"{o.customer_name} | {o.phone_1}",
                'full_address': f"{o.address or ''}, {o.tehsil or ''}, {o.district or ''}, {o.state or ''} - {o.pincode or ''}",
                'items_summary': items_desc,
                'grand_total': int(o.grand_total or 0),
                'status': o.status or "Pending",
                'whatsapp_text': wa_text,
                'primary_phone': o.phone_1,
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
        try:
            return render(request, 'admin_control.html', context)
        except Exception:
            return render(request, 'crm_core/admin_control.html', context)

    # -----------------------------------------------------------------
    # ROUTE 2: EMPLOYEE PORTAL (Normal Employee View)
    # -----------------------------------------------------------------
    if request.method == 'POST':
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
        
        grand_total = (p1_count * p1_price) + (p2_count * p2_price) + (p3_count * p3_price)
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

    # Employee Filters
    raw_emp_orders = Order.objects.filter(employee=user).order_by('-date')
    emp_start_date = request.GET.get('emp_start_date')
    emp_end_date = request.GET.get('emp_end_date')
    
    if emp_start_date and emp_end_date:
        raw_emp_orders = raw_emp_orders.filter(date__range=[emp_start_date, emp_end_date])

    emp_orders_list = []
    for o in raw_emp_orders:
        emp_orders_list.append({
            'date': o.date.strftime("%d-%m-%Y") if o.date else "",
            'customer_name': o.customer_name,
            'phone_1': o.phone_1,
            'items': f"{o.product_1_name or ''} ({o.product_1_count or 0})",
            'grand_total': int(o.grand_total or 0),
            'status': o.status or "Pending"
        })

    context = {
        'emp_orders_list': emp_orders_list,
        'emp_start_date': emp_start_date or '',
        'emp_end_date': emp_end_date or '',
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