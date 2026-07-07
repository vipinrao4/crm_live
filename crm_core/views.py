from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Order, EmployeeProfile
from django.db.models import Sum
import json

# 1. Real Login View for Employees & Admin
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'crm_core/login.html', {'form': form})

# 2. Secure Logout View
def logout_view(request):
    logout(request)
    return redirect('login')

# 3. Main Dashboard View (Protected)
@login_required(login_url='login')
def dashboard_view(request):
    is_admin = request.user.is_superuser
    summary_data = []

    # Summary data sirf tabhi calculate hoga agar login karne wala banda ADMIN hai
    if is_admin:
        employees = User.objects.filter(is_superuser=False)
        for emp in employees:
            profile, created = EmployeeProfile.objects.get_or_create(user=emp)
            ads_spent = float(profile.ads_spent)

            new_units = Order.objects.filter(employee=emp, is_repeat=False).aggregate(
                total=Sum('product_1_count') + Sum('product_2_count') + Sum('product_3_count')
            )['total'] or 0

            repeat_units = Order.objects.filter(employee=emp, is_repeat=True).aggregate(
                total=Sum('product_1_count') + Sum('product_2_count') + Sum('product_3_count')
            )['total'] or 0

            total_units = new_units + repeat_units
            avg_per_unit = round(ads_spent / total_units, 2) if total_units > 0 else 0.00

            summary_data.append({
                'username': emp.username,
                'new_units': new_units,
                'repeat_units': repeat_units,
                'total_units': total_units,
                'ads_spent': ads_spent,
                'avg_per_unit': avg_per_unit
            })

    return render(request, 'crm_core/dashboard.html', {
        'summary_data': summary_data,
        'is_admin': is_admin,
        'current_username': request.user.username
    })

# 4. Save Order API (Auto-maps logged in employee)
@login_required(login_url='login')
def save_order_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_order = Order.objects.create(
                employee=request.user, # Ab automatic logged-in employee ka naam chadh jayega
                customer_name=data.get('name'),
                phone_1=data.get('phone'),
                phone_2=data.get('phone2'),
                address=data.get('address'),
                pincode=data.get('pincode'),
                post_office=data.get('post'),
                tehsil=data.get('tehsil'),
                district=data.get('district'),
                state=data.get('state'),
                product_1_name=data.get('product_1_name'),
                product_1_count=data.get('product_1_count', 0),
                product_2_name=data.get('product_2_name'),
                product_2_count=data.get('product_2_count', 0),
                product_3_name=data.get('product_3_name'),
                product_3_count=data.get('product_3_count', 0),
                grand_total=data.get('grand_total', 0),
                is_repeat=data.get('is_repeat', False),
                status='pending'
            )
            return JsonResponse({'status': 'success', 'message': f'Order #{new_order.id} saved successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)