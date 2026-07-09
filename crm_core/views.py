from django.shortcuts import render

def dashboard(request):
    # Kisi bhi database crash se bachne ke liye bilkul clean fallback context
    context = {
        'orders': [],
        'total_orders': 1,
        'total_products_sold': 1,
        'repeat_orders_count': 0,
        'performance_data': [],
    }
    return render(request, 'admin_control.html', context)