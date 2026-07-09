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

def get_clean_int_price(value):
    try:
        return int(float(value or 0))
    except (ValueError, TypeError):
        return 0

@login_required
def dashboard(request):
    user = request.user
    
    if request.method == 'GET' and request.GET.get('search_phone_ajax'):
        target_phone = request.GET.get('search_phone_ajax').strip()
        past_order = Order.objects.filter(Q(phone_1=target_phone) | Q(phone_2=target_phone)).order_by('-date').first()
        
        if past_order:
            return JsonResponse({
                'found': True,
                'name': past_order.customer_name or "",
                'phone_1': past_order.phone_1 or "",
                'phone_2': past_order.phone_2 or "",
                'address': past_order.address or "",
                'pincode': past_order.pincode or "",
                'post_office': past_order.post_office or "",
                'tehsil': past_order.tehsil or "",
                'district': past_order.district or "Lucknow",
                'state': past_order.state or "Uttar Pradesh"
            })
        return JsonResponse({'found': False})

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

    # ROUTE 1: MASTER ADMIN CONTROL
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
        repeat_orders_units_total = 0
        
        for o in raw_orders:
            current_order_units = (getattr(o, 'product_1_count', 0) or 0) + (getattr(o, 'product_2_count', 0) or 0) + (getattr(o, 'product_3_count', 0) or 0)
            total_products_sold += current_order_units
            if getattr(o, 'order_type', 'New') == 'Repeat' or getattr(o, 'is_repeat', False):
                repeat_orders_units_total += current_order_units
                
        employees = User.objects.filter(is_staff=False)
        emp_summary = []
        for emp in employees:
            emp_orders = raw_orders.filter(employee=emp)
            emp_p_count = 0
            emp_repeat_count = 0
            for eo in emp_orders:
                eo_units = (getattr(eo, 'product_1_count', 0) or 0) + (getattr(eo, 'product_2_count', 0) or 0) + (getattr(eo, 'product_3_count', 0) or 0)
                emp_p_count += eo_units
                if getattr(eo, 'order_type', 'New') == 'Repeat' or getattr(eo, 'is_repeat', False):
                    emp_repeat_count += eo_units
            
            new_orders_units = emp_orders.count() - emp_orders.filter(Q(order_type='Repeat') | Q(is_repeat=True)).count()
            
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
            
            is_rep = False
            if getattr(o, 'order_type', '') == 'Repeat' or getattr(o, 'is_repeat', False):
                is_rep = True

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
                f"Grand Total Price: Rs. {get_clean_int_price(o.grand_total)}\n"
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
                'grand_total': get_clean_int_price(o.grand_total),
                'status': o.status or "Pending",
                'whatsapp_text': wa_text,
                'primary_phone': o.phone_1,
                'is_repeat_order': is_rep
            })
            
        context = {
            'total_orders_count': total_orders_count,
            'total_products_sold': total_products_sold,
            'repeat_orders_count': repeat_orders_units_total,  # Ab yahan Total Units jayega
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

    # ROUTE 2: EMPLOYEE PORTAL
    if request.method == 'POST':
        customer_name = request.POST.get('name')
        phone_1 = (request.POST.get('phone_1') or '').replace(" ", "")[:10]
        phone_2 = (request.POST.get('phone_2') or '').replace(" ", "")[:10]
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
        tehsil = request.POST.get('tehsil')
        post_office = request.POST.get('post')
        district = request.POST.get('district')
        state = request.POST.get('state')
        
        order_submitted_type = request.POST.get('order_type', 'New')
        
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
        is_customer_repeat = (order_submitted_type == 'Repeat') or Order.objects.filter(phone_1=phone_1).exists()

        if phone_1:
            new_order = Order.objects.create(
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
            if hasattr(new_order, 'order_type'):
                new_order.order_type = order_submitted_type
                new_order.save()
                
        return redirect('dashboard')

    raw_emp_orders = Order.objects.filter(employee=user).order_by('-date')
    emp_start_date = request.GET.get('emp_start_date')
    emp_end_date = request.GET.get('emp_end_date')
    
    if emp_start_date and emp_end_date:
        raw_emp_orders = raw_emp_orders.filter(date__range=[emp_start_date, emp_end_date])

    emp_orders_list = []
    for o in raw_emp_orders:
        resolved_type = "New"
        if getattr(o, 'order_type', '') == 'Repeat' or getattr(o, 'is_repeat', False):
            resolved_type = "Repeat"

        emp_orders_list.append({
            'id': o.id,
            'date': o.date.strftime("%d-%m-%Y") if o.date else "",
            'customer_name': o.customer_name,
            'phone_1': o.phone_1,
            'items': f"{o.product_1_name or ''} ({o.product_1_count or 0})",
            'grand_total': get_clean_int_price(o.grand_total),
            'status': o.status if o.status else "Pending",
            'order_type': resolved_type
        })

    context = {
        'emp_orders_list': emp_orders_list,
        'emp_start_date': emp_start_date or '',
        'emp_end_date': emp_end_date or '',
        'is_edit_mode': False
    }

    try:
        return render(request, 'dashboard.html', context)
    except Exception:
        return render(request, 'crm_core/dashboard.html', context)


@login_required
def edit_order_view(request, order_id):
    order_obj = get_object_or_404(Order, id=order_id, employee=request.user)
    
    if order_obj.status and order_obj.status != 'Pending':
        return redirect('dashboard')
        
    if request.method == 'POST':
        order_obj.customer_name = request.POST.get('name')
        order_obj.phone_1 = (request.POST.get('phone_1') or '').replace(" ", "")[:10]
        order_obj.phone_2 = (request.POST.get('phone_2') or '').replace(" ", "")[:10]
        order_obj.address = request.POST.get('address')
        order_obj.pincode = request.POST.get('pincode')
        order_obj.tehsil = request.POST.get('tehsil')
        order_obj.post_office = request.POST.get('post')
        
        order_obj.product_1_name = request.POST.get('product_1')
        order_obj.product_1_count = int(request.POST.get('product_1_count', 1) or 1)
        p1_price = float(request.POST.get('product_1_price', 0) or 0)
        
        order_obj.product_2_name = request.POST.get('product_2')
        order_obj.product_2_count = int(request.POST.get('product_2_count', 0) or 0)
        p2_price = float(request.POST.get('product_2_price', 0) or 0)
        
        order_obj.product_3_name = request.POST.get('product_3')
        order_obj.product_3_count = int(request.POST.get('product_3_count', 0) or 0)
        p3_price = float(request.POST.get('product_3_price', 0) or 0)
        
        order_obj.grand_total = (order_obj.product_1_count * p1_price) + \
                                (order_obj.product_2_count * p2_price) + \
                                (order_obj.product_3_count * p3_price)
                                
        order_obj.save()
        return redirect('dashboard')
        
    resolved_edit_type = "New"
    if getattr(order_obj, 'order_type', '') == 'Repeat' or getattr(order_obj, 'is_repeat', False):
        resolved_edit_type = "Repeat"

    context = {
        'order': order_obj,
        'grand_total_int': get_clean_int_price(order_obj.grand_total),
        'is_edit_mode': True,
        'order_type_resolved': resolved_edit_type
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