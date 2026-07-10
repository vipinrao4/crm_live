from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Admin panel list display fields setting
    list_display = ('id', 'customer_name', 'phone', 'total', 'status')
    list_filter = ('status',)
    search_fields = ('customer_name', 'phone')