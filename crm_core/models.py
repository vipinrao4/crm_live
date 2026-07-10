from django.db import models
from django.utils import timezone

class Order(models.Model):
    emp = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=200)
    phone1 = models.CharField(max_length=10)
    phone2 = models.CharField(max_length=10, blank=True, null=True)
    address = models.TextField()
    pincode = models.CharField(max_length=6, blank=True, null=True)
    post_office = models.CharField(max_length=100, blank=True, null=True)
    tehsil = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    
    items_summary = models.TextField()
    total_bottles = models.IntegerField(default=0)
    grand_total = models.IntegerField(default=0)
    
    is_repeat = models.BooleanField(default=False)
    status = models.CharField(max_length=50, default='Pending') # Pending, Generated, Cancelled
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.phone1}"