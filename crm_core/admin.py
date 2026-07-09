{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="container-fluid mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>Master Admin Control <span class="badge bg-danger fs-6">All Access</span></h2>
        <a href="{% url 'logout' %}" class="btn btn-outline-danger btn-sm">Logout</a>
    </div>

    <div class="row g-3 mb-4">
        <div class="col-md-4">
            <div class="card p-3 shadow-sm border-start border-danger border-4">
                <small class="text-muted fw-bold d-block mb-1">Filtered Total Orders</small>
                <h3 class="text-danger mb-0">{{ total_orders }}</h3>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card p-3 shadow-sm border-start border-primary border-4">
                <small class="text-muted fw-bold d-block mb-1">Filtered Total Products Sold (Units)</small>
                <h3 class="text-primary mb-0">{{ total_products_sold }} Units</h3>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card p-3 shadow-sm border-start border-warning border-4">
                <small class="text-muted fw-bold d-block mb-1">Repeat Orders Counter (Units)</small>
                <h3 class="text-warning mb-0">{{ repeat_orders_count }} Units</h3>
            </div>
        </div>
    </div>

    <div class="card shadow-sm p-3 mb-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4 class="mb-0 fw-bold text-dark">Employee Performance Summary</h4>
        </div>
        <div class="table-responsive">
            <table class="table table-hover align-middle bg-white border mb-0">
                <thead class="table-light text-muted small text-uppercase">
                    <tr>
                        <th>Employee Name</th>
                        <th>New Orders (Product Count)</th>
                        <th>Repeat Orders (Product Count)</th>
                        <th>Total Products Sold</th>
                        <th>Ads Spent (₹)</th>
                        <th>Avg Cost / Unit (₹)</th>
                    </tr>
                </thead>
                <tbody class="small">
                    <tr>
                        <td class="fw-bold text-dark">dummyemp</td>
                        <td>1</td>
                        <td>0 Units</td>
                        <td>1 Units</td>
                        <td><input type="number" class="form-control form-control-sm d-inline-block text-center bg-light border-0" value="0" style="width: 80px;" disabled></td>
                        <td class="fw-bold">₹0.00</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <div class="card shadow-sm p-3 mb-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4 class="mb-0 fw-bold text-dark">Master Order Log</h4>
        </div>
        <div class="table-responsive">
            <table class="table table-hover align-middle bg-white border mb-0">
                <thead class="table-light text-muted small text-uppercase">
                    <tr>
                        <th style="width: 40px;"><input type="checkbox" class="form-check-input"></th>
                        <th>Date</th>
                        <th>Emp</th>
                        <th>Customer & Contacts</th>
                        <th>Full Address</th>
                        <th>Items Summary</th>
                        <th>Grand Total</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody class="small">
                    {% for order in orders %}
                    <tr>
                        <td><input type="checkbox" class="form-check-input"></td>
                        <td class="text-muted">{{ order.date|date:"d-m-Y" }}</td>
                        <td><span class="badge bg-secondary px-2 py-1">{{ order.emp }}</span></td>
                        <td class="fw-bold text-dark">{{ order.customer_name }} | {{ order.phone }}</td>
                        <td class="text-muted text-truncate" style="max-width: 250px;">{{ order.address }}</td>
                        <td>{{ order.items }}</td>
                        <td class="fw-bold text-dark">₹{{ order.total }}</td>
                        <td><span class="badge bg-success">{{ order.status }}</span></td>
                    </tr>
                    {% empty %}
                    <tr class="table-success-light">
                        <td><input type="checkbox" class="form-check-input"></td>
                        <td class="text-muted">09-07-2026</td>
                        <td><span class="badge bg-secondary px-2 py-1">dummyemp</span></td>
                        <td class="fw-bold text-dark">test | 9999988888</td>
                        <td class="text-muted text-truncate" style="max-width: 250px;">56, Lucknow, Lucknow, Uttar Pradesh - 226017</td>
                        <td>Asthakesri (x1)</td>
                        <td class="fw-bold text-dark">₹1300</td>
                        <td><span class="badge bg-success">Generated</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}