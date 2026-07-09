from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def dashboard(request):
    # Dynamic Routing: Agar user employee hai (staff nahi hai), toh use employee page par bhejo
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('emp_dashboard')

    # ADMIN LOGIC
    try:
        orders = Order.objects.all().order_by('-id')
        total_orders = orders.count()
    except Exception:
        orders = []
        total_orders = 0

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'total_products_sold': total_orders,
        'repeat_orders_count': 0,
    }
    return render(request, 'crm_core/admin_control.html', context)


@login_required
def emp_dashboard_view(request):
    # Strict Check: Agar koi admin galti se yahan aaye toh use handle karein
    username = request.user.username
    
    # Handle New Order Punching (POST Request)
    message = ""
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        items = request.POST.get('items')
        total = request.POST.get('total', 0)
        
        try:
            Order.objects.create(
                emp=username,
                customer_name=customer_name,
                phone=phone,
                address=address,
                items=items,
                total=total,
                status='Generated'
            )
            message = "success"
        except Exception as e:
            message = f"error: {str(e)}"

    # Fetch employee's own punched orders
    try:
        my_orders = Order.objects.filter(emp=username).order_by('-id')
    except Exception:
        my_orders = []

    # Standalone HTML Rendering for Employee Dashboard (No template file required!)
    from django.http import HttpResponse
    
    success_alert = '<div class="alert alert-success">Order successfully punch ho gaya!</div>' if message == "success" else ""
    error_alert = f'<div class="alert alert-danger">{message}</div>' if "error" in message else ""
    
    orders_rows = ""
    for order in my_orders:
        orders_rows += f"""
        <tr>
            <td>{order.date.strftime('%d-%m-%Y') if order.date else '09-07-2026'}</td>
            <td><b>{order.customer_name}</b><br><small class="text-muted">{order.phone}</small></td>
            <td>{order.address}</td>
            <td>{order.items}</td>
            <td>₹{order.total}</td>
            <td><span class="badge bg-success">{order.status}</span></td>
        </tr>
        """
    
    if not orders_rows:
        orders_rows = """<tr><td colspan="6" class="text-center text-muted">Abhi tak aapne koi order punch nahi kiya hai.</td></tr>"""

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Employee Dashboard - Divjot CRM</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f4f6f9; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }}
            .card {{ border: none; border-radius: 12px; }}
        </style>
    </head>
    <body>
        <div class="container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4 p-3 bg-white shadow-sm rounded">
                <h4 class="mb-0 fw-bold text-dark">Divjot CRM - Employee Portal (<span class="text-danger">{username}</span>)</h4>
                <a href="/accounts/logout/" class="btn btn-outline-danger btn-sm fw-bold">Logout</a>
            </div>
            
            {success_alert}
            {error_alert}

            <div class="row g-4">
                <div class="col-md-4">
                    <div class="card p-4 shadow-sm bg-white">
                        <h5 class="fw-bold mb-3 text-dark">Punch New Order</h5>
                        <form method="POST">
                            <input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get('CSRF_COOKIE', '')}">
                            <div class="mb-3">
                                <label class="form-label small fw-bold text-muted">Customer Name</label>
                                <input type="text" name="customer_name" class="form-control form-control-sm" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label small fw-bold text-muted">Phone Number</label>
                                <input type="text" name="phone" class="form-control form-control-sm" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label small fw-bold text-muted">Full Address</label>
                                <textarea name="address" class="form-control form-control-sm" rows="3" required></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label small fw-bold text-muted">Items Summary</label>
                                <input type="text" name="items" class="form-control form-control-sm" placeholder="e.g. Asthakesri (x1)" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label small fw-bold text-muted">Grand Total (₹)</label>
                                <input type="number" name="total" class="form-control form-control-sm" required>
                            </div>
                            <button type="submit" class="btn btn-danger w-100 btn-sm fw-bold mt-2">Submit Order</button>
                        </form>
                    </div>
                </div>

                <div class="col-md-8">
                    <div class="card p-4 shadow-sm bg-white">
                        <h5 class="fw-bold mb-3 text-dark">My Punched Orders Log</h5>
                        <div class="table-responsive">
                            <table class="table table-hover align-middle border mb-0 small">
                                <thead class="table-light text-uppercase text-muted">
                                    <tr>
                                        <th>Date</th>
                                        <th>Customer</th>
                                        <th>Address</th>
                                        <th>Items</th>
                                        <th>Total</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {orders_rows}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)