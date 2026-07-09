from django.urls import path
from divjot_crm_backend.urls import simple_login_bypass

urlpatterns = [
    path('', simple_login_bypass, name='dashboard'),
]