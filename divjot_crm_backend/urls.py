from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from crm_core import views as crm_views

urlpatterns = [
    # Status update path ko default admin se pehle rakha hai taaki 404 na aaye
    path('update-status/<int:order_id>/', crm_views.admin_update_status, name='admin_update_status'),
    
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='crm_core/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
    
    path('', include('crm_core.urls')),
]