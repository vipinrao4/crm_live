from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views # Ye add karo
from crm_core import views

urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'), # Ye add karo
    path('update-status/<int:order_id>/', views.admin_update_status, name='admin_update_status'),
    path('admin/', admin.site.urls),
    path('', include('crm_core.urls')),
]