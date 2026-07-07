from django.contrib import admin
from .models import Order, EmployeeProfile

# Admin panel me Orders table ko acche se dikhane ke liye
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'employee', 'customer_name', 'phone_1', 'grand_total', 'status', 'is_repeat')
    list_filter = ('status', 'is_repeat', 'date', 'employee')
    search_fields = ('customer_name', 'phone_1', 'phone_2', 'pincode')

# Admin panel me Employee Profile ko active karne ke liye
admin.site.register(EmployeeProfile)