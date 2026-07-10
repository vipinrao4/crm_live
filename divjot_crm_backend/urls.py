from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from crm_core import views

urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('update-status/<int:order_id>/', views.admin_update_status, name='admin_update_status'),
    path('admin/', admin.site.urls),
    path('', include('crm_core.urls')),
]