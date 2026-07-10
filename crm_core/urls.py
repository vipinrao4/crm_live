from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'), # Admin Panel
    path('employee/dashboard/', views.emp_dashboard_view, name='emp_dashboard'), # Emp Panel
    path('logout/', views.custom_logout, name='logout'), # NAYA LOGOUT ROUTE
    path('update-status/<int:order_id>/', views.admin_update_status, name='admin_update_status'),
]