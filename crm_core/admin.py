<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Master Admin Control - Divjot CRM</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
        .card { border: none; border-radius: 10px; }
    </style>
</head>
<body>

<div class="container-fluid mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4 p-3 bg-white shadow-sm rounded">
        <h2 class="mb-0 fs-3 fw-bold text-dark">Master Admin Control <span class="badge bg-danger fs-6 ms-2">All Access</span></h2>
        <a href="/accounts/logout/" class="btn btn-outline-danger btn-sm fw-bold">Logout</a>
    </div>

    <!-- COUNTER CARDS -->
    <div class="row g-3 mb-4">
        <div class="col-md-4">
            <div class="card p-3 shadow-sm bg-white border-start border-danger border-4">
                <small class="text-muted fw-bold d-block mb-1 text-uppercase small">Total Orders</small>
                <h3 class="text-danger mb-0 fw-bold">{{ total_orders }}</h3>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card p-3 shadow-sm bg-white border-start border-primary border-4">
                <small class="text-muted fw-bold d-block mb-1 text-uppercase small">Total Products Sold</small>
                <h3 class="text-primary mb-0 fw-bold">{{ total_products_sold }} Units</h3>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card p-3 shadow-sm bg-white border-start border-warning border-4">
                <small class="text-muted fw-bold d-block mb-1 text-uppercase small">Repeat Orders</small>
                <h3 class="text-warning mb-0 fw-bold">{{ repeat_orders_count }} Units</h3>
            </div>
        </div>
    </div>

    <!-- MASTER ORDER LOG -->
    <div class="card shadow-sm p-3 mb-4 bg-white">
        <div class="mb-3">
            <h5 class="mb-0 fw-bold text-dark">Master Order Log</h5>
        </div>
        <div class="table-responsive">
            <table class="table table-hover align-middle border mb-0">
                <thead class="table-light text-muted small text-uppercase">
                    <tr>
                        <th>Date</th>
                        <th>Emp</th>
                        <th>Customer & Contacts</th>
                        <th>Full Address</th>
                        <th>Items Summary</th>
                        <th>Grand Total</th>
                        <th>Status / Live Action Controls</th>
                    </tr>
                </thead>
                <tbody class="small">
                    {% for order in orders %}
                    <tr>
                        <td class="text-muted">{{ order.date|date:"d-m-Y" }}</td>
                        <!-- Fixed field variable bindings here -->
                        <td><span class="badge bg-secondary px-2 py-1">{{ order.emp.username|default:order.emp }}</span></td>
                        <td class="fw-bold text-dark">{{ order.customer_name }} | {{ order.phone }}</td>
                        <td class="text-muted">{{ order.address }}</td>
                        <td class="fw-semibold text-secondary">{{ order.items }}</td>
                        <td class="fw-bold text-dark">₹{{ order.total }}</td>
                        <td>
                            <div class="mb-1">
                                {% if order.status == 'Pending' %}
                                    <span class="badge bg-warning text-dark text-uppercase">Pending</span>
                                {% elif order.status == 'Generated' %}
                                    <span class="badge bg-success text-uppercase">Generated</span>
                                {% else %}
                                    <span class="badge bg-danger text-uppercase">Cancelled</span>
                                {% endif %}
                            </div>
                            <form method="POST" action="/admin/update-status/{{ order.id }}/" class="d-inline">
                                {% csrf_token %}
                                <button type="submit" name="status" value="Generated" class="btn btn-success btn-xs py-0 px-1 text-white fw-bold me-1" style="font-size: 11px; background-color: #198754;">Generate</button>
                                <button type="submit" name="status" value="Cancelled" class="btn btn-danger btn-xs py-0 px-1 text-white fw-bold me-1" style="font-size: 11px;">Cancel</button>
                            </form>
                            <a href="https://api.whatsapp.com/send?phone={{ order.phone }}&text=Hello%20{{ order.customer_name }},%20Aapka%20order%20{{ order.items }}%20confirm%20ho%20gaya%20hai." target="_blank" class="btn btn-info btn-xs py-0 px-1 text-white bg-dark border-0 fw-bold" style="font-size: 11px;">WhatsApp</a>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="7" class="text-center text-muted py-3">No orders found.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

</body>
</html>