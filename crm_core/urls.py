from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),            # Yeh aapka admin dashboard ka raasta hai
    path('', include('crm_core.urls')),       # Yeh employee portal ko connect karega
]