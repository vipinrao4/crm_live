from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login as django_login
from django.http import JsonResponse
from .models import Order
from django.db.models import Q

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

@user_passes_test(is_admin, login_url='/accounts/login/')
def dashboard(request):
    return render(request, 'crm_core/admin_control.html', {'orders': Order.objects.all().order_by('-id')})

@login_required(login_url='/accounts/login/')
def emp_dashboard_view(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.GET.get('action') == 'search_phone':
        q = request.GET.get('phone', '')
        o = Order.objects.filter(Q(phone__icontains=q)).first()
        return JsonResponse({'status': 'success', 'name': o.customer_name, 'address': o.address, 'total': o.total} if o else {'status': 'not_found'})
    
    return render(request, 'crm_core/dashboard.html', {'orders': Order.objects.all().order_by('-id')})

@login_required(login_url='/accounts/login/')
def admin_update_status(request, order_id):
    if request.method == 'POST':
        o = Order.objects.get(id=order_id)
        o.status = request.POST.get('status')
        o.save()
    return redirect('/')