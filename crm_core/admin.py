from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Dynamic display safe methods taaki admin panel kabhi crash na ho field mismatch se
    list_display = ('id', 'customer_name', 'get_phone', 'get_total', 'status')
    list_filter = ('status',)
    search_fields = ('customer_name',)

    def get_phone(self, obj):
        # Database mein phone ya customer_phone jo bhi field ho, yeh use dhoodh lega
        return getattr(obj, 'phone', getattr(obj, 'customer_phone', 'No Phone'))
    get_phone.short_description = 'Phone Number'

    def get_total(self, obj):
        # Database mein total ya grand_total jo bhi field ho, yeh use dhoodh lega
        return f"₹{getattr(obj, 'total', getattr(obj, 'grand_total', 0))}"
    get_total.short_description = 'Grand Total'