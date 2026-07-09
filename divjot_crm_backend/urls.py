from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

# Kisi bhi built-in Django LoginView ko bypass karne ke liye direct function view
def simple_login_bypass(request):
    context = {
        'orders': [],
        'total_orders': 1,
        'total_products_sold': 1,
        'repeat_orders_count': 0,
    }
    return render(request, 'crm_core/admin_control.html', context)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', simple_login_bypass, name='login'),
    path('accounts/logout/', simple_login_bypass, name='logout'),
    path('', include('crm_core.urls')),
]