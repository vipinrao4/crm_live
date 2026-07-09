from django.contrib import admin
from .models import Order

# Bina kisi explicit field list ke simple registration taaki crash hone ka 0% chance rahe
admin.site.register(Order)