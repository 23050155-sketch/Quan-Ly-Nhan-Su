// ====== COMMON & AUTH CHECK ======
const token = localStorage.getItem(TOKEN_KEY);
const userInfo = JSON.parse(localStorage.getItem(USER_INFO_KEY) || "{}");

if (!token) {
    window.location.href = "/html/login.html";
}

// nếu lỡ admin mở nhầm trang employee-home thì quăng về admin-dashboard
if (userInfo.role === "admin") {
    window.location.href = ADMIN_DASHBOARD_URL;
}

const employeeId = userInfo.employee_id;
const welcomeText = document.getElementById("welcomeText");
welcomeText.textContent = `Xin chào, ${userInfo.username || "nhân viên"}`;

// ====== NAV TABS ======
const tabs = document.querySelectorAll(".tab");
const views = {
    profile: document.getElementById("view-profile"),
    attendance: document.getElementById("view-attendance"),
    leaves: document.getElementById("view-leaves"),
    payroll: document.getElementById("view-payroll"),
    performance: document.getElementById("view-performance"),
};

function showView(name) {
    tabs.forEach(t => t.classList.toggle("active", t.dataset.view === name));
    Object.entries(views).forEach(([k, el]) => {
        if (el) el.classList.toggle("active", k === name);
    });

    if (name === "profile") loadProfile();
    if (name === "attendance") loadAttendance();
    if (name === "leaves") loadLeaves();
    if (name === "payroll") loadPayroll();
    if (name === "performance") loadPerformance();
}

tabs.forEach(tab => {
    tab.addEventListener("click", () => {
        const name = tab.dataset.view;
        showView(name);
    });
});

// ====== LOGOUT ======
document.getElementById("btnLogout").addEventListener("click", () => {
    localStorage.clear();
    window.location.href = "/html/login.html";
});

// ====== API HELPERS ======
async function apiGet(path) {
    const res = await fetch(`${API_BASE_URL}${path}`, {
        headers: {
            "Authorization": `Bearer ${token}`,
        },
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

// ====== PROFILE ======
const profileCard = document.getElementById("profileCard");

async function loadProfile() {
    if (!employeeId) {
        profileCard.innerHTML = `<p>Chưa gắn Employee ID cho tài khoản này.</p>`;
        return;
    }

    try {
        const emp = await apiGet(`/employees/${employeeId}`);
        profileCard.innerHTML = `
            <p><strong>Họ tên:</strong> ${emp.full_name || ""}</p>
            <p><strong>Email:</strong> ${emp.email || ""}</p>
            <p><strong>Số điện thoại:</strong> ${emp.phone || ""}</p>
            <p><strong>Giới tính:</strong> ${emp.gender || ""}</p>
            <p><strong>Phòng ban:</strong> ${emp.department || ""}</p>
            <p><strong>Chức vụ:</strong> ${emp.position || ""}</p>
            <p><strong>Ngày vào làm:</strong> ${emp.start_date || ""}</p>
        `;
    } catch (err) {
        console.error(err);
        profileCard.innerHTML = `<p>Không tải được thông tin nhân viên.</p>`;
    }
}

// ====== ATTENDANCE ======
const attForm = document.getElementById("attFilterForm");
const attTableBody = document.querySelector("#attTable tbody");

async function loadAttendance() {
    try {
        const fromDate = document.getElementById("attFromDate").value;
        const toDate = document.getElementById("attToDate").value;

        const params = new URLSearchParams();
        // nếu backend yêu cầu employee_id thì thêm vô:
        if (employeeId) params.append("employee_id", employeeId);

        const data = await apiGet(`/attendances?${params.toString()}`);

        attTableBody.innerHTML = "";
        data.forEach(a => {
            // filter theo ngày nếu có chọn
            if (fromDate && a.date < fromDate) return;
            if (toDate && a.date > toDate) return;

            const tr = document.createElement("tr");
            tr.innerHTML = `
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

// ====== LEAVES ======
const leaveCreateForm = document.getElementById("leaveCreateForm");
const leavesTableBody = document.querySelector("#leavesTable tbody");

async function loadLeaves() {
    try {
        // gọi luôn kèm employee_id cho chắc
        const params = new URLSearchParams();
        if (employeeId) params.append("employee_id", employeeId);

        const data = await apiGet(`/leaves?${params.toString()}`);
        leavesTableBody.innerHTML = "";
        data.forEach(l => {
            const period = `${l.start_date} → ${l.end_date}`;
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${period}</td>
                <td>${l.reason || ""}</td>
                <td>${l.status}</td>
            `;
            leavesTableBody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        alert("Không tải được danh sách đơn nghỉ");
    }
}

leaveCreateForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const start = document.getElementById("leaveStart").value;
    const end = document.getElementById("leaveEnd").value;
    const reason = document.getElementById("leaveReason").value.trim();

    if (!start || !end) {
        alert("Vui lòng chọn đầy đủ thời gian nghỉ.");
        return;
    }
    if (end < start) {
        alert("Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu.");
        return;
    }

    try {
        await apiPost("/leaves", {
            employee_id: employeeId,   // ✅ gửi kèm employee_id
            start_date: start,
            end_date: end,
            reason: reason || null,
        });
        alert("Gửi đơn nghỉ thành công");
        leaveCreateForm.reset();
        loadLeaves();
    } catch (err) {
        console.error(err);
        alert("Không gửi được đơn nghỉ");
    }
});

// ====== PAYROLL ======
const payFilterForm = document.getElementById("payFilterForm");
const payTableBody = document.querySelector("#payTable tbody");

async function loadPayroll() {
    try {
        const year = document.getElementById("payYearFilter").value;
        const month = document.getElementById("payMonthFilter").value;

        const params = new URLSearchParams();
        if (employeeId) params.append("employee_id", employeeId);
        if (year) params.append("year", year);
        if (month) params.append("month", month);

        const data = await apiGet(`/payrolls?${params.toString()}`);

        payTableBody.innerHTML = "";
        data.forEach(p => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${p.month}/${p.year}</td>
                <td>${p.attendance_days}</td>
                <td>${p.paid_leave_days}</td>
                <td>${p.base_daily_salary.toLocaleString("vi-VN")}</td>
                <td>${p.gross_salary.toLocaleString("vi-VN")}</td>
                <td>${p.deductions.toLocaleString("vi-VN")}</td>
                <td>${p.net_salary.toLocaleString("vi-VN")}</td>
                <td>
                    <button class="btn-secondary btn-sm"
                        data-year="${p.year}"
                        data-month="${p.month}">
                        Tải PDF
                    </button>
                </td>
            `;
            payTableBody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        alert("Không tải được dữ liệu lương");
    }
}

payFilterForm.addEventListener("submit", (e) => {
    e.preventDefault();
    loadPayroll();
});

// tải phiếu lương PDF
payTableBody.addEventListener("click", (e) => {
    const btn = e.target.closest("button");
    if (!btn) return;

    const year = btn.dataset.year;
    const month = btn.dataset.month;

    if (!year || !month || !employeeId) return;

    const url = `${API_BASE_URL}/reports/payroll-slip-pdf?year=${year}&month=${month}&employee_id=${employeeId}`;

    fetch(url, {
        headers: {
            "Authorization": `Bearer ${token}`,
        },
    })
        .then(res => {
            if (!res.ok) throw new Error("Download error");
            return res.blob();
        })
        .then(blob => {
            const link = document.createElement("a");
            const fileUrl = URL.createObjectURL(blob);
            link.href = fileUrl;
            link.download = `phieu_luong_${month}_${year}.pdf`;
            document.body.appendChild(link);
            link.click();
            link.remove();
            URL.revokeObjectURL(fileUrl);
        })
        .catch(err => {
            console.error(err);
            alert("Không tải được phiếu lương");
        });
});

// ====== PERFORMANCE REVIEWS (ĐÁNH GIÁ) ======
const perfSummaryCard = document.getElementById("perfSummaryCard");
const perfTableBody = document.querySelector("#perfTable tbody");

async function loadPerformance() {
    if (!perfSummaryCard || !perfTableBody) return;

    if (!employeeId) {
        perfSummaryCard.innerHTML = `<p>Chưa gắn Employee ID cho tài khoản này.</p>`;
        perfTableBody.innerHTML = "";
        return;
    }

    try {
        // với role employee: backend tự filter theo current_user.employee_id
        const data = await apiGet("/performance-reviews");

        // Nếu không có đánh giá nào
        if (!data || data.length === 0) {
            perfSummaryCard.innerHTML = `
                <p>Hiện tại bạn chưa có đánh giá hiệu suất nào.</p>
            `;
            perfTableBody.innerHTML = "";
            return;
        }

        // Lấy review mới nhất (backend đã order created_at DESC)
        const latest = data[0];

        // Tính điểm trung bình
        const avg =
            data.reduce((sum, r) => sum + (r.score || 0), 0) / data.length;

        perfSummaryCard.innerHTML = `
            <p><strong>Kỳ đánh giá gần nhất:</strong> ${latest.period}</p>
            <p><strong>Điểm kỳ gần nhất:</strong> ${latest.score}/5</p>
            <p><strong>Điểm kỳ gần nhất:</strong> ${"⭐".repeat(latest.score)}${"☆".repeat(5 - latest.score)}</p>
            <p><strong>Tóm tắt:</strong> ${latest.summary || "Không có mô tả"}</p>
        `;

        // render bảng lịch sử
        perfTableBody.innerHTML = "";
        data.forEach(r => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${r.period}</td>
                <td>${"⭐".repeat(r.score)}${"☆".repeat(5 - r.score)}</td>
                <td>${r.summary || ""}</td>
                <td>${r.strengths || ""}</td>
                <td>${r.improvements || ""}</td>
                <td>${r.created_at ? new Date(r.created_at).toLocaleString("vi-VN") : ""}</td>
            `;
            perfTableBody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        perfSummaryCard.innerHTML = `<p>Không tải được dữ liệu đánh giá. Vui lòng thử lại sau.</p>`;
        perfTableBody.innerHTML = "";
        alert("Không tải được dữ liệu đánh giá hiệu suất");
    }
}


// ====== INIT ======
showView("profile");
