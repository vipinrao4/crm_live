from django.db import models
from django.contrib.auth.models import User

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Har employee ke aage admin uski ads spent memory manually feed kar sakega
    ads_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.username

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generated', 'Generated'),
        ('cancelled', 'Cancelled'),
    ]

    date = models.DateField(auto_now_add=True)
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    
    # Customer and Contact fields (Dual phone support)
    customer_name = models.CharField(max_length=255)
    phone_1 = models.CharField(max_length=15)
    phone_2 = models.CharField(max_length=15)
    
    # Full Address structure
    address = models.TextField()
    pincode = models.CharField(max_length=6)
    post_office = models.CharField(max_length=100)
    tehsil = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    
    # Product Rows (Up to 3 multi-product choices)
    product_1_name = models.CharField(max_length=100, blank=True, null=True)
    product_1_count = models.IntegerField(default=0)
    
    product_2_name = models.CharField(max_length=100, blank=True, null=True)
    product_2_count = models.IntegerField(default=0)
    
    product_3_name = models.CharField(max_length=100, blank=True, null=True)
    product_3_count = models.IntegerField(default=0)
    
    # Totals and Indicators
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_repeat = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order {self.id} - {self.customer_name}"