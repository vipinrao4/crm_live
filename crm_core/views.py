from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order
from django.db.models import Q
from datetime import datetime

@login_required
def dashboard(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('emp_dashboard')

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
    username = request.user.username
    message = ""
    
    # 1. HANDLE NEW ORDER SUBMISSION WITH TWO PHONES & POSTAL DETAILS
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        phone1 = request.POST.get('phone1', '').strip()
        phone2 = request.POST.get('phone2', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        post_office = request.POST.get('post_office', '').strip()
        district = request.POST.get('district', '').strip()
        state = request.POST.get('state', '').strip()
        address_line = request.POST.get('address_line', '').strip()
        items = request.POST.get('items')
        total = request.POST.get('total', 0)
        
        # Combine everything into a single structured address block
        full_address = f"{address_line}, PO: {post_office}, Dist: {district}, {state} - {pincode}"
        combined_phones = f"{phone1} / {phone2}" if phone2 else phone1
        
        try:
            Order.objects.create(
                emp=username,
                customer_name=customer_name,
                phone=combined_phones,
                address=full_address,
                items=items,
                total=total,
                status='Generated'
            )
            message = "success"
        except Exception as e:
            message = f"error: {str(e)}"

    # 2. GET FILTERS & SEARCH QUERY
    search_phone = request.GET.get('search_phone', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()

    orders_query = Order.objects.all()

    if search_phone:
        orders_query = orders_query.filter(
            Q(phone__icontains=search_phone) | Q(customer_name__icontains=search_phone)
        )

    if start_date and end_date:
        try:
            s_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            e_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            orders_query = orders_query.filter(date__range=[s_date, e_date])
        except Exception:
            pass

    try:
        my_orders = orders_query.order_by('-id')
        all_existing_phones = list(Order.objects.values_list('phone', flat=True))
    except Exception:
        my_orders = []
        all_existing_phones = []

    # 3. PARSE EXISTING PHONES TO DETECT REPEATS
    # We create a simple dictionary/set of raw numbers that appear more than once in the DB
    raw_phone_pool = []
    for p in all_existing_phones:
        for num in p.split('/'):
            num_clean = num.strip()
            if num_clean:
                raw_phone_pool.append(num_clean)
                
    # Phone numbers that already exist across database
    from collections import Counter
    phone_counts = Counter(raw_phone_pool)

    # 4. COUNTERS FOR FILTERS
    total_orders_count = len(my_orders)
    total_sales_amount = 0
    repeat_counter = 0

    for o in my_orders:
        try:
            total_sales_amount += float(o.total or 0)
        except ValueError:
            pass

    # 5. COMPILE TABLE ROWS WITH LIVE REPEAT CHECKING LOGIC
    orders_rows = ""
    for order in my_orders:
        order_date_str = order.date.strftime('%d-%m-%Y') if order.date else '09-07-2026'
        emp_badge = order.emp if order.emp else 'System'
        
        # Check if any part of the phone string constitutes a repeat buyer
        is_repeat = False
        for segment in order.phone.split('/'):
            seg_clean = segment.strip()
            if seg_clean and phone_counts[seg_clean] > 1:
                is_repeat = True
                break
        
        status_display = f'<span class="badge bg-success px-2 py-1 text-uppercase">{order.status}</span>'
        if is_repeat:
            repeat_counter += 1
            status_display += '<br><span class="badge bg-warning text-dark px-2 py-1 text-uppercase fw-bold mt-1">⚠️ REPEAT</span>'

        orders_rows += f"""
        <tr>
            <td class="text-muted">{order_date_str}</td>
            <td><span class="badge bg-secondary px-2 py-1">{emp_badge}</span></td>
            <td><b>{order.customer_name}</b><br><small class="text-muted">{order.phone}</small></td>
            <td class="text-wrap" style="max-width: 220px;">{order.address}</td>
            <td>{order.items}</td>
            <td class="fw-bold text-dark">₹{order.total}</td>
            <td>{status_display}</td>
        </tr>
        """
    
    if not orders_rows:
        orders_rows = """<tr><td colspan="7" class="text-center text-muted py-4">Koi order logs nahi mile.</td></tr>"""

    # 6. HTML COMPILATION WITH INTEGRATED POSTAL API JAVASCRIPT
    from django.http import HttpResponse
    
    success_alert = '<div class="alert alert-success fw-bold shadow-sm mb-3">➔ Order successfully punch ho gaya aur repeat metrics update ho gaye hain!</div>' if message == "success" else ""
    error_alert = f'<div class="alert alert-danger fw-bold shadow-sm mb-3">⚠️ Error: {message}</div>' if "error" in message else ""
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Employee Portal - Divjot CRM</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f4f6f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
            .card {{ border: none; border-radius: 12px; }}
            .form-control:focus {{ border-color: #dc3545; box-shadow: 0 0 0 0.25rem rgba(220, 53, 69, 0.25); }}
            .badge-repeat {{ background-color: #ffc107; color: #000; }}
        </style>
    </head>
    <body>
        <div class="container-fluid px-4 mt-4">
            <!-- PORTAL HEADER -->
            <div class="d-flex justify-content-between align-items-center mb-4 p-3 bg-white shadow-sm rounded">
                <h4 class="mb-0 fw-bold text-dark">Divjot CRM - Employee Portal (<span class="text-danger">{username}</span>)</h4>
                <a href="/accounts/logout/" class="btn btn-outline-danger btn-sm fw-bold px-3">Logout</a>
            </div>
            
            {success_alert}
            {error_alert}

            <!-- METRICS CARDS -->
            <div class="row g-3 mb-4">
                <div class="col-md-4">
                    <div class="card p-3 shadow-sm bg-white border-start border-danger border-4">
                        <small class="text-muted fw-bold d-block mb-1 text-uppercase small">Total Filtered Orders</small>
                        <h3 class="text-danger mb-0 fw-bold">{total_orders_count}</h3>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card p-3 shadow-sm bg-white border-start border-primary border-4">
                        <small class="text-muted fw-bold d-block mb-1 text-uppercase small">Total Sales Volume</small>
                        <h3 class="text-primary mb-0 fw-bold">₹{total_sales_amount:,.2f}</h3>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card p-3 shadow-sm bg-white border-start border-warning border-4">
                        <small class="text-muted fw-bold d-block mb-1 text-uppercase small">Total Repeat Orders Count</small>
                        <h3 class="text-warning mb-0 fw-bold">{repeat_counter} Orders</h3>
                    </div>
                </div>
            </div>

            <!-- FILTERS & LOOKUP UTILITIES -->
            <div class="row g-3 mb-4">
                <div class="col-md-6">
                    <div class="card p-3 shadow-sm bg-white">
                        <label class="form-label fw-bold text-muted small">Filter Logs By Range</label>
                        <form method="GET" class="d-flex gap-2">
                            <input type="date" name="start_date" value="{start_date}" class="form-control form-control-sm">
                            <input type="date" name="end_date" value="{end_date}" class="form-control form-control-sm">
                            <button type="submit" class="btn btn-dark btn-sm px-3 fw-bold">Apply</button>
                            <a href="?" class="btn btn-outline-secondary btn-sm fw-bold">Reset</a>
                        </form>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card p-3 shadow-sm bg-white">
                        <label class="form-label fw-bold text-muted small">Search Customer Ledger</label>
                        <form method="GET" class="input-group input-group-sm">
                            <input type="text" name="search_phone" value="{search_phone}" class="form-control" placeholder="Search by name or phone number...">
                            <button type="submit" class="btn btn-danger px-3 fw-bold">Search</button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- MAIN WORKING SECTION -->
            <div class="row g-4">
                <!-- FORM CONTAINER -->
                <div class="col-xl-4 col-lg-5">
                    <div class="card p-4 shadow-sm bg-white">
                        <h5 class="fw-bold mb-3 text-dark border-bottom pb-2">Punch New Entry</h5>
                        <form method="POST" id="orderForm">
                            <input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get('CSRF_COOKIE', '')}">
                            
                            <div class="mb-2">
                                <label class="form-label small fw-bold text-muted mb-1">Customer Full Name</label>
                                <input type="text" name="customer_name" class="form-control form-control-sm" required placeholder="Enter buyer name">
                            </div>

                            <div class="row g-2 mb-2">
                                <div class="col-6">
                                    <label class="form-label small fw-bold text-muted mb-1">Phone Number 1 (Req)</label>
                                    <input type="text" name="phone1" id="phone1" maxlength="10" minlength="10" class="form-control form-control-sm" required placeholder="10-digit primary">
                                </div>
                                <div class="col-6">
                                    <label class="form-label small fw-bold text-muted mb-1">Phone Number 2 (Opt)</label>
                                    <input type="text" name="phone2" id="phone2" maxlength="10" class="form-control form-control-sm" placeholder="10-digit optional">
                                </div>
                            </div>

                            <div class="row g-2 mb-2">
                                <div class="col-4">
                                    <label class="form-label small fw-bold text-muted mb-1">Pincode</label>
                                    <input type="text" name="pincode" id="pincode" maxlength="6" class="form-control form-control-sm" required placeholder="6 digit">
                                </div>
                                <div class="col-8">
                                    <label class="form-label small fw-bold text-muted mb-1">Post Office</label>
                                    <select name="post_office" id="post_office" class="form-select form-select-sm" required>
                                        <option value="">Enter pincode first</option>
                                    </select>
                                </div>
                            </div>

                            <div class="row g-2 mb-2">
                                <div class="col-6">
                                    <label class="form-label small fw-bold text-muted mb-1">District</label>
                                    <input type="text" name="district" id="district" class="form-control form-control-sm" readonly required>
                                </div>
                                <div class="col-6">
                                    <label class="form-label small fw-bold text-muted mb-1">State</label>
                                    <input type="text" name="state" id="state" class="form-control form-control-sm" readonly required>
                                </div>
                            </div>

                            <div class="mb-2">
                                <label class="form-label small fw-bold text-muted mb-1">House No. / Gali / Colony Address</label>
                                <input type="text" name="address_line" class="form-control form-control-sm" required placeholder="Flat number, Street name...">
                            </div>

                            <div class="mb-2">
                                <label class="form-label small fw-bold text-muted mb-1">Product Items Summary</label>
                                <input type="text" name="items" class="form-control form-control-sm" placeholder="e.g. Asthakesri (x1)" required>
                            </div>

                            <div class="mb-3">
                                <label class="form-label small fw-bold text-muted mb-1">Grand Total Final Price (₹)</label>
                                <input type="number" name="total" class="form-control form-control-sm" required placeholder="0.00">
                            </div>

                            <button type="submit" class="btn btn-danger w-100 btn-sm fw-bold py-2">Submit and Save Order ➔</button>
                        </form>
                    </div>
                </div>

                <!-- LIVE DATALOG -->
                <div class="col-xl-8 col-lg-7">
                    <div class="card p-4 shadow-sm bg-white">
                        <h5 class="fw-bold mb-3 text-dark border-bottom pb-2">Master Orders Log Database</h5>
                        <div class="table-responsive">
                            <table class="table table-hover align-middle border mb-0 small">
                                <thead class="table-light text-uppercase text-muted" style="font-size: 11px;">
                                    <tr>
                                        <th>Date</th>
                                        <th>Agent</th>
                                        <th>Customer & Phones</th>
                                        <th>Shipping Address</th>
                                        <th>Products</th>
                                        <th>Total Price</th>
                                        <th>Status States</th>
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

        <!-- CLIENT SIDE VALIDATION AND AUTO-LOOKUP CODE -->
        <script>
            // strict 10 digit constraint checking
            document.getElementById('orderForm').addEventListener('submit', function(e) {{
                const p1 = document.getElementById('phone1').value;
                const p2 = document.getElementById('phone2').value;
                
                if(p1.length !== 10 || isNaN(p1)) {{
                    alert('Error: Phone Number 1 poora 10 digit ka hona chahiye!');
                    e.preventDefault();
                    return;
                }}
                if(p2.length > 0 && (p2.length !== 10 || isNaN(p2))) {{
                    alert('Error: Phone Number 2 galat hai! Ya toh khali chhodein ya poora 10 digit daalein.');
                    e.preventDefault();
                }}
            }});

            // Pincode Lookup API handling
            document.getElementById('pincode').addEventListener('input', function() {{
                const pin = this.value.trim();
                if(pin.length === 6) {{
                    const poSelect = document.getElementById('post_office');
                    poSelect.innerHTML = '<option value="">Loading locations...</option>';
                    
                    fetch(`https://api.postalpincode.in/pincode/${{pin}}`)
                    .then(res => res.json())
                    .then(data => {{
                        if(data[0].Status === "Success") {{
                            const postOffices = data[0].PostOffice;
                            poSelect.innerHTML = '';
                            
                            postOffices.forEach(po => {{
                                const opt = document.createElement('option');
                                opt.value = po.Name;
                                opt.innerText = po.Name;
                                poSelect.appendChild(opt);
                            }});
                            
                            document.getElementById('district').value = postOffices[0].District;
                            document.getElementById('state').value = postOffices[0].State;
                        }} else {{
                            poSelect.innerHTML = '<option value="">Galat pincode!</option>';
                            document.getElementById('district').value = '';
                            document.getElementById('state').value = '';
                        }}
                    }})
                    .catch(err => {{
                        poSelect.innerHTML = '<option value="">Error fetching data</option>';
                    }});
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HttpResponse(html_content)