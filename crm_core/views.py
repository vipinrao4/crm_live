from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .models import Order
from django.db.models import Q

def custom_login(request):
    # Agar pehle se login hai, toh seedha andar bhejo
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('/')
        return redirect('/employee/dashboard/')

    error_msg = None
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        # Django Auth check
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user) # Session create ho gaya
            
            # Admin hai toh admin panel, warna employee panel
            if user.is_staff or user.is_superuser:
                return redirect('/')
            else:
                return redirect('/employee/dashboard/')
        else:
            error_msg = "Invalid Username or Password!"
            
    return render(request, 'crm_core/login.html', {'error': error_msg})

@login_required(login_url='/accounts/login/')
def dashboard(request):
    # Agar employee galti se admin par aaye toh wapas bhejo
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('/employee/dashboard/')
        
    return render(request, 'crm_core/admin_control.html', {})

@login_required(login_url='/accounts/login/')
def emp_dashboard_view(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.GET.get('action') == 'search_phone':
        q = request.GET.get('phone', '')
        o = Order.objects.filter(Q(phone__icontains=q)).first()
        return JsonResponse({'status': 'success', 'name': o.customer_name, 'address': o.address, 'total': o.total} if o else {'status': 'not_found'})
        
    return render(request, 'crm_core/dashboard.html', {'orders': Order.objects.all()})

@login_required(login_url='/accounts/login/')
def admin_update_status(request, order_id):
    if request.method == 'POST':
        o = Order.objects.get(id=order_id)
        o.status = request.POST.get('status')
        o.save()
    return redirect('/')