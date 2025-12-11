// ====== AUTH & COMMON ======
const token = localStorage.getItem(TOKEN_KEY);
const userInfo = JSON.parse(localStorage.getItem(USER_INFO_KEY) || "{}");

if (!token) {
    window.location.href = "/html/login.html";
}

if (userInfo.role !== "admin") {
    // Không phải admin thì quăng về trang nhân viên
    window.location.href = EMPLOYEE_HOME_URL;
}

document.getElementById("adminName").textContent =
    userInfo.username || "Admin";

// ---------- NAV & VIEW ----------
const navLinks = document.querySelectorAll(".sidebar nav a[data-view]");
const views = {
    dashboard: document.getElementById("view-dashboard"),
    users: document.getElementById("view-users"),
    employees: document.getElementById("view-employees"),
    attendance: document.getElementById("view-attendance"),
    leaves: document.getElementById("view-leaves"),
    payroll: document.getElementById("view-payroll"),
    reports: document.getElementById("view-reports"),
    performance: document.getElementById("view-performance"),
};
const pageTitle = document.getElementById("pageTitle");

let attendanceChartInstance = null; // dùng cho Chart.js (Reports)

function showView(name) {
    Object.entries(views).forEach(([key, el]) => {
        if (el) el.classList.toggle("active", key === name);
    });

    navLinks.forEach(link => {
        const v = link.dataset.view;
        link.classList.toggle("active", v === name);
    });

    switch (name) {
        case "dashboard":
            pageTitle.textContent = "Dashboard";
            loadDashboard();
            break;
        case "users":
            pageTitle.textContent = "Users";
            loadUsers();
            break;
        case "employees":
            pageTitle.textContent = "Employees";
            loadEmployees();
            break;
        case "attendance":
            pageTitle.textContent = "Attendance";
            loadAttendance();
            break;
        case "leaves":
            pageTitle.textContent = "Leave Requests";
            loadLeaves();
            break;
        case "payroll":
            pageTitle.textContent = "Payroll";
            loadPayroll();
            break;
        case "performance":                         
            pageTitle.textContent = "Performance";  
            loadPerformance();                      
            break;
        case "reports":
            pageTitle.textContent = "Reports";
            loadAttendanceChart(); // load chart khi mở tab Reports
            break;
    }
}

navLinks.forEach(link => {
    link.addEventListener("click", (e) => {
        e.preventDefault();
        const view = link.dataset.view;
        if (view) showView(view);
    });
});

// ---------- LOGOUT ----------
document.getElementById("logoutBtn").addEventListener("click", (e) => {
    e.preventDefault();
    localStorage.clear();
    window.location.href = "/html/login.html";
});

// ---------- COMMON FETCH HELPER ----------
async function apiGet(path) {
    const res = await fetch(`${API_BASE_URL}${path}`, {
        headers: { "Authorization": `Bearer ${token}` },
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `GET ${path} failed`);
    }
    return res.json();
}

async function apiPost(path, body) {
    const res = await fetch(`${API_BASE_URL}${path}`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `POST ${path} failed`);
    }
    return res.json();
}

async function apiPut(path, body) {
    const res = await fetch(`${API_BASE_URL}${path}`, {
        method: "PUT",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: body ? JSON.stringify(body) : null,
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `PUT ${path} failed`);
    }
    return res.json();
}

async function apiDelete(path) {
    const res = await fetch(`${API_BASE_URL}${path}`, {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${token}`,
        },
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `DELETE ${path} failed`);
    }
    return res.json();
}

// ---------- DASHBOARD ----------
async function loadDashboard() {
    try {
        const data = await apiGet("/stats/overview");
        document.getElementById("totalEmployees").textContent =
            data.total_employees;
        document.getElementById("todayAttendance").textContent =
            data.todays_attendance_count;
        document.getElementById("pendingLeaves").textContent =
            data.pending_leave_requests;
        document.getElementById("totalSalary").textContent =
            data.current_month_total_payroll.toLocaleString("vi-VN") + " đ";
    } catch (err) {
        console.error(err);
        alert("Không tải được dữ liệu dashboard");
    }
}

// =====================================================================
//                              USERS
// =====================================================================
const usersTableBody = document.querySelector("#usersTable tbody");
const userForm = document.getElementById("userForm");
const btnReloadUsers = document.getElementById("btnReloadUsers");
const btnResetUserForm = document.getElementById("btnResetUserForm");

function resetUserForm() {
    userForm.reset();
    document.getElementById("userId").value = "";
}

async function loadUsers() {
    try {
        const users = await apiGet("/users");
        usersTableBody.innerHTML = "";
        users.forEach(u => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${u.id}</td>
                <td>${u.username}</td>
                <td>${u.role}</td>
                <td>${u.employee_id || ""}</td>
                <td>
                    <button class="btn-secondary btn-sm" data-action="edit" data-id="${u.id}">Sửa</button>
                    <button class="btn-secondary btn-sm" data-action="delete" data-id="${u.id}">Xóa</button>
                </td>
            `;
            usersTableBody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        alert("Không tải được danh sách user");
    }
}

usersTableBody.addEventListener("click", async (e) => {
    const btn = e.target.closest("button");
    if (!btn) return;

    const id = btn.dataset.id;
    const action = btn.dataset.action;

    if (action === "edit") {
        try {
            const u = await apiGet(`/users/${id}`);
            document.getElementById("userId").value = u.id;
            document.getElementById("userUsername").value = u.username;
            document.getElementById("userRole").value = u.role;
            document.getElementById("userEmployeeId").value = u.employee_id || "";
            document.getElementById("userPassword").value = ""; // không show password
        } catch (err) {
            console.error(err);
            alert("Không lấy được user");
        }
    }

    if (action === "delete") {
        if (!confirm("Xóa user này?")) return;
        try {
            await apiDelete(`/users/${id}`);
            await loadUsers();
        } catch (err) {
            console.error(err);
            alert("Không xóa được user");
        }
    }
});

userForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const id = document.getElementById("userId").value;
    const payload = {
        username: document.getElementById("userUsername").value.trim(),
        role: document.getElementById("userRole").value,
        employee_id: document.getElementById("userEmployeeId").value || null,
        email: null,
    };

    const password = document.getElementById("userPassword").value.trim();
    if (password) payload.password = password;

    if (!payload.username) {
        alert("Username không được trống");
        return;
    }

    try {
        if (id) {
            await apiPut(`/users/${id}`, payload);
        } else {
            if (!password) {
                alert("Phải nhập password khi tạo user mới");
                return;
            }
            await apiPost("/users", payload);
        }
        resetUserForm();
        await loadUsers();
    } catch (err) {
        console.error(err);
        alert("Không lưu được user (trùng username hoặc lỗi dữ liệu)");
    }
});

btnReloadUsers.addEventListener("click", (e) => {
    e.preventDefault();
    loadUsers();
});

btnResetUserForm.addEventListener("click", (e) => {
    e.preventDefault();
    resetUserForm();
});

// =====================================================================
//                              EMPLOYEES
// =====================================================================
const employeesTableBody = document.querySelector("#employeesTable tbody");
const empForm = document.getElementById("employeeForm");
const btnReloadEmployees = document.getElementById("btnReloadEmployees");
const btnResetEmployeeForm = document.getElementById("btnResetEmployeeForm");

function resetEmployeeForm() {
    empForm.reset();
    document.getElementById("empId").value = "";
}

async function loadEmployees() {
    try {
        const employees = await apiGet("/employees");
        employeesTableBody.innerHTML = "";
        employees.forEach(emp => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${emp.id}</td>
                <td>${emp.full_name}</td>
                <td>${emp.email || ""}</td>
                <td>${emp.phone || ""}</td>
                <td>${emp.department || ""}</td>
                <td>${emp.position || ""}</td>
                <td>${emp.start_date || ""}</td>
                <td>
                    <button class="btn-secondary btn-sm" data-action="edit" data-id="${emp.id}">Sửa</button>
                    <button class="btn-secondary btn-sm" data-action="delete" data-id="${emp.id}">Xóa</button>
                </td>
            `;
            employeesTableBody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        alert("Không tải được danh sách nhân viên");
    }
}

employeesTableBody.addEventListener("click", async (e) => {
    const btn = e.target.closest("button");
    if (!btn) return;
    const id = btn.dataset.id;
    const action = btn.dataset.action;

    if (action === "edit") {
        try {
            const emp = await apiGet(`/employees/${id}`);
            document.getElementById("empId").value = emp.id;
            document.getElementById("empFullName").value = emp.full_name || "";
            document.getElementById("empEmail").value = emp.email || "";
            document.getElementById("empPhone").value = emp.phone || "";
            document.getElementById("empGender").value = emp.gender || "";
            document.getElementById("empDepartment").value = emp.department || "";
            document.getElementById("empPosition").value = emp.position || "";
            document.getElementById("empStartDate").value = emp.start_date || "";
        } catch (err) {
            console.error(err);
            alert("Không lấy được thông tin nhân viên");
        }
    } else if (action === "delete") {
        if (!confirm("Xóa nhân viên này?")) return;
        try {
            await apiDelete(`/employees/${id}`);
            await loadEmployees();
        } catch (err) {
            console.error(err);
            alert("Không xóa được nhân viên");
        }
    }
});

empForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("empId").value;
    const payload = {
        full_name: document.getElementById("empFullName").value.trim(),
        email: document.getElementById("empEmail").value.trim() || null,
        phone: document.getElementById("empPhone").value.trim() || null,
        gender: document.getElementById("empGender").value || null,
        department: document.getElementById("empDepartment").value.trim() || null,
        position: document.getElementById("empPosition").value.trim() || null,
        start_date: document.getElementById("empStartDate").value || null,
    };

    if (!payload.full_name) {
        alert("Họ tên không được trống");
        return;
    }

    try {
        if (id) {
            await apiPut(`/employees/${id}`, payload);
        } else {
            await apiPost("/employees", payload);
        }
        resetEmployeeForm();
        await loadEmployees();
    } catch (err) {
        console.error(err);
        alert("Không lưu được nhân viên (check quyền admin & dữ liệu)");
    }
});

btnReloadEmployees.addEventListener("click", (e) => {
    e.preventDefault();
    loadEmployees();
});
btnResetEmployeeForm.addEventListener("click", (e) => {
    e.preventDefault();
    resetEmployeeForm();
});

// =====================================================================
//                              ATTENDANCE
// =====================================================================
const attForm = document.getElementById("attendanceFilterForm");
const attTableBody = document.querySelector("#attendanceTable tbody");

async function loadAttendance() {
    try {
        const empId = document.getElementById("attEmployeeId").value;
        const dateVal = document.getElementById("attDate").value;

        const params = new URLSearchParams();
        if (empId) params.append("employee_id", empId);
        if (dateVal) params.append("work_date", dateVal);

        const data = await apiGet(`/attendances?${params.toString()}`);
        attTableBody.innerHTML = "";
        data.forEach(a => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${a.id}</td>
                <td>${a.employee_id}</td>
                <td>${a.date}</td>
                <td>${a.check_in || ""}</td>
                <td>${a.check_out || ""}</td>
            `;
            attTableBody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        alert("Không tải được dữ liệu chấm công");
    }
}

attForm.addEventListener("submit", (e) => {
    e.preventDefault();
    loadAttendance();
});

// =====================================================================
//                              LEAVES
// =====================================================================
const leaveForm = document.getElementById("leaveFilterForm");
const leavesTableBody = document.querySelector("#leavesTable tbody");

async function loadLeaves() {
    try {
        const empId = document.getElementById("leaveEmployeeId").value;
        const status = document.getElementById("leaveStatus").value;

        const params = new URLSearchParams();
        if (empId) params.append("employee_id", empId);
        if (status) params.append("leave_status", status);

        const data = await apiGet(`/leaves?${params.toString()}`);
        leavesTableBody.innerHTML = "";
        data.forEach(l => {
            const period = `${l.start_date} → ${l.end_date}`;
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${l.id}</td>
                <td>${l.employee_id}</td>
                <td>${period}</td>
                <td>${l.reason || ""}</td>
                <td>${l.status}</td>
                <td>
                    ${l.status === "pending" ? `
                        <button class="btn-primary btn-sm" data-action="approve" data-id="${l.id}">Approve</button>
                        <button class="btn-secondary btn-sm" data-action="reject" data-id="${l.id}">Reject</button>
                    ` : ""}
                </td>
            `;
            leavesTableBody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        alert("Không tải được đơn nghỉ");
    }
}

leavesTableBody.addEventListener("click", async (e) => {
    const btn = e.target.closest("button");
    if (!btn) return;
    const id = btn.dataset.id;
    const action = btn.dataset.action;

    try {
        if (action === "approve") {
            await apiPut(`/leaves/${id}/approve`);
        } else if (action === "reject") {
            await apiPut(`/leaves/${id}/reject`);
        }
        await loadLeaves();
    } catch (err) {
        console.error(err);
        alert("Không cập nhật được trạng thái đơn nghỉ");
    }
});

leaveForm.addEventListener("submit", (e) => {
    e.preventDefault();
    loadLeaves();
});

// =====================================================================
//                              PAYROLL
// =====================================================================
const payrollCalcForm = document.getElementById("payrollCalcForm");
const payrollFilterForm = document.getElementById("payrollFilterForm");
const payrollTableBody = document.querySelector("#payrollTable tbody");

async function loadPayroll() {
    try {
        const empId = document.getElementById("filterPayEmployeeId").value;
        const year = document.getElementById("filterPayYear").value;
        const month = document.getElementById("filterPayMonth").value;

        const params = new URLSearchParams();
        if (empId) params.append("employee_id", empId);
        if (year) params.append("year", year);
        if (month) params.append("month", month);

        const data = await apiGet(`/payrolls?${params.toString()}`);
        payrollTableBody.innerHTML = "";
        data.forEach(p => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${p.id}</td>
                <td>${p.employee_id}</td>
                <td>${p.month}/${p.year}</td>
                <td>${p.attendance_days}</td>
                <td>${p.paid_leave_days}</td>
                <td>${p.base_daily_salary.toLocaleString("vi-VN")}</td>
                <td>${p.gross_salary.toLocaleString("vi-VN")}</td>
                <td>${p.deductions.toLocaleString("vi-VN")}</td>
                <td>${p.net_salary.toLocaleString("vi-VN")}</td>
            `;
            payrollTableBody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        alert("Không tải được bảng lương");
    }
}

payrollCalcForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
        employee_id: Number(document.getElementById("payEmployeeId").value),
        year: Number(document.getElementById("payYear").value),
        month: Number(document.getElementById("payMonth").value),
        base_daily_salary: Number(document.getElementById("payDailySalary").value),
        deductions: Number(document.getElementById("payDeductions").value || 0),
    };

    if (!payload.employee_id || !payload.year || !payload.month) {
        alert("Vui lòng nhập đầy đủ employee, năm, tháng");
        return;
    }

    try {
        await apiPost("/payrolls/calculate", payload);
        alert("Tính lương thành công");
        await loadPayroll();
    } catch (err) {
        console.error(err);
        alert("Không tính được lương (kiểm tra trùng bảng lương, quyền admin, dữ liệu)");
    }
});

payrollFilterForm.addEventListener("submit", (e) => {
    e.preventDefault();
    loadPayroll();
});

// =====================================================================
//                          PERFORMANCE REVIEWS
// =====================================================================
const performanceTableBody = document.querySelector("#performanceTable tbody");
const performanceForm = document.getElementById("performanceForm");
const btnReloadPerformance = document.getElementById("btnReloadPerformance");
const btnResetPerformanceForm = document.getElementById("btnResetPerformanceForm");

function resetPerformanceForm() {
    if (!performanceForm) return;
    performanceForm.reset();
    const idInput = document.getElementById("perfId");
    if (idInput) idInput.value = "";
}

async function loadPerformance() {
    if (!performanceTableBody) return;

    try {
        const empFilter = document.getElementById("perfFilterEmployeeId")?.value;
        const params = new URLSearchParams();
        if (empFilter) params.append("employee_id", empFilter);

        const data = await apiGet(`/performance-reviews?${params.toString()}`);
        performanceTableBody.innerHTML = "";

        data.forEach(pr => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${pr.id}</td>
                <td>${pr.employee_id}</td>
                <td>${pr.period}</td>
                <td>${"⭐".repeat(pr.score)}${"☆".repeat(5 - pr.score)}</td>
                <td>${pr.summary || ""}</td>
                <td>${pr.created_at || ""}</td>
                <td>
                    <button class="btn-secondary btn-sm" data-action="edit" data-id="${pr.id}">Sửa</button>
                    <button class="btn-secondary btn-sm" data-action="delete" data-id="${pr.id}">Xóa</button>
                </td>
            `;
            performanceTableBody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        alert("Không tải được danh sách performance review");
    }
}

// click edit/delete trên bảng
if (performanceTableBody) {
    performanceTableBody.addEventListener("click", async (e) => {
        const btn = e.target.closest("button");
        if (!btn) return;

        const id = btn.dataset.id;
        const action = btn.dataset.action;

        if (action === "edit") {
            try {
                const pr = await apiGet(`/performance-reviews/${id}`);
                document.getElementById("perfId").value = pr.id;
                document.getElementById("perfEmployeeId").value = pr.employee_id;
                document.getElementById("perfPeriod").value = pr.period;
                document.getElementById("perfScore").value = pr.score;
                document.getElementById("perfSummary").value = pr.summary || "";
                document.getElementById("perfStrengths").value = pr.strengths || "";
                document.getElementById("perfImprovements").value = pr.improvements || "";
            } catch (err) {
                console.error(err);
                alert("Không lấy được dữ liệu đánh giá");
            }
        }

        if (action === "delete") {
            if (!confirm("Xóa đánh giá này?")) return;
            try {
                await apiDelete(`/performance-reviews/${id}`);
                await loadPerformance();
            } catch (err) {
                console.error(err);
                alert("Không xóa được đánh giá");
            }
        }
    });
}

// submit form create / update
if (performanceForm) {
    performanceForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const id = document.getElementById("perfId").value;
        const payload = {
            employee_id: Number(document.getElementById("perfEmployeeId").value),
            period: document.getElementById("perfPeriod").value.trim(),
            score: Number(document.getElementById("perfScore").value),
            summary: document.getElementById("perfSummary").value.trim() || null,
            strengths: document.getElementById("perfStrengths").value.trim() || null,
            improvements: document.getElementById("perfImprovements").value.trim() || null,
        };

        if (!payload.employee_id || !payload.period || !payload.score) {
            alert("Vui lòng nhập Employee ID, Period, Score");
            return;
        }

        try {
            if (id) {
                await apiPut(`/performance-reviews/${id}`, payload);
            } else {
                await apiPost("/performance-reviews", payload);
            }
            resetPerformanceForm();
            await loadPerformance();
        } catch (err) {
            console.error(err);
            alert("Không lưu được performance review (check quyền admin / dữ liệu)");
        }
    });
}

// nút reload + reset
if (btnReloadPerformance) {
    btnReloadPerformance.addEventListener("click", (e) => {
        e.preventDefault();
        loadPerformance();
    });
}
if (btnResetPerformanceForm) {
    btnResetPerformanceForm.addEventListener("click", (e) => {
        e.preventDefault();
        resetPerformanceForm();
    });
}


// =====================================================================
//                              REPORTS
// =====================================================================

// helper download có kèm token
async function downloadFile(path, filename) {
    try {
        const res = await fetch(`${API_BASE_URL}${path}`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!res.ok) {
            const text = await res.text();
            console.error("Download error:", res.status, text);
            alert("Không tải được file (kiểm tra quyền admin / token).");
            return;
        }

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();

        a.remove();
        URL.revokeObjectURL(url);
    } catch (err) {
        console.error(err);
        alert("Có lỗi khi tải file.");
    }
}

document.getElementById("btnExportPayrollExcel")
    .addEventListener("click", () => {
        downloadFile("/reports/payroll-excel", "bang_luong.xlsx");
    });

document.getElementById("btnExportPayrollPdf")
    .addEventListener("click", () => {
        downloadFile("/reports/payroll-pdf", "bang_luong.pdf");
    });

document.getElementById("btnExportAttendanceExcel")
    .addEventListener("click", () => {
        downloadFile("/reports/attendance-excel", "cham_cong.xlsx");
    });

// ----- Attendance Chart -----
async function loadAttendanceChart() {
    const yearInput = document.getElementById("chartYear");
    const monthInput = document.getElementById("chartMonth");
    const canvas = document.getElementById("attendanceChart");
    if (!yearInput || !monthInput || !canvas) return;

    // Nếu không nhập, dùng năm/tháng hiện tại
    const now = new Date();
    const year = yearInput.value || now.getFullYear();
    const month = monthInput.value || (now.getMonth() + 1);

    // Gán lại lên input cho user thấy luôn
    yearInput.value = year;
    monthInput.value = month;

    const params = new URLSearchParams();
    params.append("year", year);
    params.append("month", month);

    try {
        const data = await apiGet(`/stats/attendance-summary?${params.toString()}`);

        // data expected: { year, month, items: [{ employee_id, days }, ...] }
        const labels = (data.items || []).map(i => `Emp ${i.employee_id}`);
        const values = (data.items || []).map(i => i.days);

        const ctx = canvas.getContext("2d");

        if (attendanceChartInstance) {
            attendanceChartInstance.destroy();
        }

        attendanceChartInstance = new Chart(ctx, {
            type: "bar",
            data: {
                labels,
                datasets: [
                    {
                        label: `Số ngày đi làm (${data.month}/${data.year})`,
                        data: values,
                    },
                ],
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1,
                        },
                    },
                },
            },
        });
    } catch (err) {
        console.error(err);
        alert("Không tải được dữ liệu biểu đồ chấm công");
    }
}

const attendanceChartForm = document.getElementById("attendanceChartForm");
if (attendanceChartForm) {
    attendanceChartForm.addEventListener("submit", (e) => {
        e.preventDefault();
        loadAttendanceChart();
    });
}

// =====================================================================
//                              INIT
// =====================================================================
showView("dashboard");
