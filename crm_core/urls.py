from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'), # Admin dashboard (root)
    path('employee/dashboard/', views.emp_dashboard_view, name='emp_dashboard'),
]