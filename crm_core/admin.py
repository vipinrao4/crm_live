from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Ekdum clear aur safe listing jo kabhi crash nahi hogi
    list_display = ('id', 'customer_name', 'status')
    list_filter = ('status',)
    search_fields = ('customer_name',)