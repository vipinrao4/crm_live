<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Master Admin Control - Divjot CRM</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { bg-color: #f8f9fa; }
        .border-start-danger { border-left: 4px solid #dc3545 !important; }
        .border-start-primary { border-left: 4px solid #0d6efd !important; }
        .border-start-warning { border-left: 4px solid #ffc107 !important; }
    </style>
</head>
<body>

<div class="container-fluid mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>Master Admin Control <span class="badge bg-danger fs-6">All Access</span></h2>
        <a href="/admin/logout/" class="btn btn-outline-danger btn-sm">Logout</a>
    </div>

    <div class="row g-3 mb-4">
        <div class="col-md-4">
            <div class="card p-3 shadow-sm border-start-danger">
                <small class="text-muted fw-bold d-block mb-1">Filtered Total Orders</small>
                <h3 class="text-danger mb-0">1</h3>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card p-3 shadow-sm border-start-primary">
                <small class="text-muted fw-bold d-block mb-1">Filtered Total Products Sold (Units)</small>
                <h3 class="text-primary mb-0">1 Units</h3>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card p-3 shadow-sm border-start-warning">
                <small class="text-muted fw-bold d-block mb-1">Repeat Orders Counter (Units)</small>
                <h3 class="text-warning mb-0">0 Units</h3>
            </div>
        </div>
    </div>

    <div class="card shadow-sm p-3 mb-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4 class="mb-0 fw-bold text-dark">Employee Performance Summary</h4>
            <button onclick="exportTableToExcel('empPerformanceTable', 'Employee_Performance_Report')" class="btn btn-success btn-sm shadow-sm fw-bold">
                💾 Export Performance to Excel
            </button>
        </div>
        <div class="table-responsive">
            <table class="table table-hover align-middle bg-white border mb-0" id="empPerformanceTable">
                <thead class="table-light text-muted small text-uppercase">
                    <tr>
                        <th>Employee Name</th>
                        <th>New Orders (Product Count)</th>
                        <th>Repeat Orders (Product Count)</th>
                        <th>Total Products Sold</th>
                        <th>Ads Spent (₹) [Input Values]</th>
                        <th>Avg Cost / Unit (₹) [Formula]</th>
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
            <button onclick="exportTableToExcel('masterOrderLogTable', 'Master_Order_Log_Report')" class="btn btn-success btn-sm shadow-sm fw-bold">
                💾 Export Orders to Excel
            </button>
        </div>
        <div class="table-responsive">
            <table class="table table-hover align-middle bg-white border mb-0" id="masterOrderLogTable">
                <thead class="table-light text-muted small text-uppercase">
                    <tr>
                        <th style="width: 40px;"><input type="checkbox" class="form-check-input"></th>
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
                    <tr class="table-success-light">
                        <td><input type="checkbox" class="form-check-input"></td>
                        <td class="text-muted">09-07-2026</td>
                        <td><span class="badge bg-secondary px-2 py-1">dummyemp</span></td>
                        <td class="fw-bold text-dark">test | 9999988888</td>
                        <td class="text-muted text-truncate" style="max-width: 250px;">56, Lucknow, Lucknow, Uttar Pradesh - 226017</td>
                        <td>Asthakesri (x1)</td>
                        <td class="fw-bold text-dark">₹1300</td>
                        <td>
                            <span class="badge bg-success px-2 py-1 me-1 text-uppercase">Generated</span>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
<script>
function exportTableToExcel(tableID, filename = '') {
    var tableSelect = document.getElementById(tableID);
    var wb = XLSX.utils.table_to_book(tableSelect, {sheet: "Sheet1"});
    var wbout = XLSX.write(wb, {bookType: 'xlsx', type: 'binary'});
    function s2ab(s) {
        var buf = new ArrayBuffer(s.length);
        var view = new Uint8Array(buf);
        for (var i=0; i<s.length; i++) view[i] = s.charCodeAt(i) & 0xFF;
        return buf;
    }
    var blob = new Blob([s2ab(wbout)], {type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8'});
    filename = filename ? filename + '.xlsx' : 'Report.xlsx';
    var downloadLink = document.createElement("a");
    downloadLink.href = window.URL.createObjectURL(blob);
    downloadLink.download = filename;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}
</script>
</body>
</html>