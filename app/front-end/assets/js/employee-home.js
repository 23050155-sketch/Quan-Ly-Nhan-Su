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
    // 🔥 THÊM COMPLIANCE VIEW
    compliance: document.getElementById("view-compliance"),
};

function showView(name) {
    tabs.forEach((t) => t.classList.toggle("active", t.dataset.view === name));
    Object.entries(views).forEach(([k, el]) => {
        if (el) el.classList.toggle("active", k === name);
    });

    if (name === "profile") loadProfile();
    if (name === "attendance") loadAttendance();
    if (name === "leaves") loadLeaves();
    if (name === "payroll") loadPayroll();
    if (name === "performance") loadPerformance();
    if (name === "compliance") loadCompliance(); // 🔥 gọi Compliance
}

tabs.forEach((tab) => {
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
            Authorization: `Bearer ${token}`,
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
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `POST ${path} failed`);
    }
    // với acknowledge policy API trả 204 → không có body
    if (res.status === 204) return;
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
        if (employeeId) params.append("employee_id", employeeId);

        const data = await apiGet(`/attendances?${params.toString()}`);

        attTableBody.innerHTML = "";
        data.forEach((a) => {
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
        const params = new URLSearchParams();
        if (employeeId) params.append("employee_id", employeeId);

        const data = await apiGet(`/leaves?${params.toString()}`);
        leavesTableBody.innerHTML = "";
        data.forEach((l) => {
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
            employee_id: employeeId,
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
        data.forEach((p) => {
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
            Authorization: `Bearer ${token}`,
        },
    })
        .then((res) => {
            if (!res.ok) throw new Error("Download error");
            return res.blob();
        })
        .then((blob) => {
            const link = document.createElement("a");
            const fileUrl = URL.createObjectURL(blob);
            link.href = fileUrl;
            link.download = `phieu_luong_${month}_${year}.pdf`;
            document.body.appendChild(link);
            link.click();
            link.remove();
            URL.revokeObjectURL(fileUrl);
        })
        .catch((err) => {
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
        const data = await apiGet("/performance-reviews");

        if (!data || data.length === 0) {
            perfSummaryCard.innerHTML = `
                <p>Hiện tại bạn chưa có đánh giá hiệu suất nào.</p>
            `;
            perfTableBody.innerHTML = "";
            return;
        }

        const latest = data[0];
        const avg =
            data.reduce((sum, r) => sum + (r.score || 0), 0) / data.length;

        perfSummaryCard.innerHTML = `
            <p><strong>Kỳ đánh giá gần nhất:</strong> ${latest.period}</p>
            <p><strong>Điểm kỳ gần nhất:</strong> ${latest.score}/5</p>
            <p><strong>Đánh giá sao:</strong> ${"⭐".repeat(latest.score)}${"☆".repeat(5 - latest.score)}</p>
            <p><strong>Tóm tắt:</strong> ${latest.summary || "Không có mô tả"}</p>
        `;

        perfTableBody.innerHTML = "";
        data.forEach((r) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${r.period}</td>
                <td>${"⭐".repeat(r.score)}${"☆".repeat(5 - r.score)}</td>
                <td>${r.summary || ""}</td>
                <td>${r.strengths || ""}</td>
                <td>${r.improvements || ""}</td>
                <td>${
                    r.created_at
                        ? new Date(r.created_at).toLocaleString("vi-VN")
                        : ""
                }</td>
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

// ====== COMPLIANCE – EMPLOYEE ======
const myComplianceTbody = document.getElementById("myComplianceTbody");

// modal elements
const complianceModal = document.getElementById("complianceModal");
const compModalTitle = document.getElementById("compModalTitle");
const compModalMeta = document.getElementById("compModalMeta");
const compModalDesc = document.getElementById("compModalDesc");
const compModalAckBtn = document.getElementById("compModalAckBtn");
const compModalClose = document.getElementById("compModalClose");
const compModalClose2 = document.getElementById("compModalClose2");

let compliancePolicyMap = new Map(); // id -> policy
let currentPolicyId = null;

function openComplianceModal(policy) {
    if (!complianceModal) return;

    currentPolicyId = policy.id;

    compModalTitle.textContent = policy.title || "Compliance Policy";

    const code = policy.code ? `• Mã: ${policy.code}` : "";
    const eff = policy.effective_date ? `• Hiệu lực: ${policy.effective_date}` : "";
    const status = policy.is_acknowledged
        ? `• Trạng thái: Đã xác nhận${policy.acknowledged_at ? " (" + new Date(policy.acknowledged_at).toLocaleString("vi-VN") + ")" : ""}`
        : "• Trạng thái: Chưa xác nhận";

    compModalMeta.textContent = [code, eff, status].filter(Boolean).join("  ");

    // description có thể null
    const desc = (policy.description || "").trim();
    compModalDesc.textContent = desc || "Policy này chưa có nội dung mô tả.";

    // nút xác nhận chỉ hiện khi chưa ack
    if (compModalAckBtn) compModalAckBtn.style.display = policy.is_acknowledged ? "none" : "inline-flex";

    complianceModal.classList.add("show");
    complianceModal.setAttribute("aria-hidden", "false");
}

function closeComplianceModal() {
    if (!complianceModal) return;
    complianceModal.classList.remove("show");
    complianceModal.setAttribute("aria-hidden", "true");
    currentPolicyId = null;
}

if (compModalClose) compModalClose.addEventListener("click", closeComplianceModal);
if (compModalClose2) compModalClose2.addEventListener("click", closeComplianceModal);

// click vào nền để đóng
if (complianceModal) {
    complianceModal.addEventListener("click", (e) => {
        if (e.target === complianceModal) closeComplianceModal();
    });
}

document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeComplianceModal();
});

async function loadCompliance() {
    if (!myComplianceTbody) return;

    myComplianceTbody.innerHTML = `<tr><td colspan="5">Đang tải...</td></tr>`;
    try {
        const policies = await apiGet("/compliance/my-policies");
        compliancePolicyMap = new Map((policies || []).map(p => [p.id, p]));

        if (!policies.length) {
            myComplianceTbody.innerHTML = `<tr><td colspan="5">Hiện chưa có chính sách nào.</td></tr>`;
            return;
        }

        myComplianceTbody.innerHTML = "";
        policies.forEach((p) => {
            const tr = document.createElement("tr");
            const effectiveDate = p.effective_date || "";

            let statusText = p.is_acknowledged ? "Đã xác nhận" : "Chưa xác nhận";

            // action: luôn có "Xem nội dung"
            // nếu chưa ack → thêm nút "Xác nhận"
            const viewBtn = `<button class="btn-small" data-action="view" data-id="${p.id}">Xem nội dung</button>`;
            const ackBtn = p.is_acknowledged
                ? (p.acknowledged_at
                    ? `<span class="badge-success">Đã đọc • ${new Date(p.acknowledged_at).toLocaleString("vi-VN")}</span>`
                    : `<span class="badge-success">Đã đọc</span>`)
                : `<button class="btn-small" data-action="ack" data-id="${p.id}">Xác nhận</button>`;

            tr.innerHTML = `
                <td>${p.title}</td>
                <td>${p.code || ""}</td>
                <td>${effectiveDate}</td>
                <td>${statusText}</td>
                <td style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                    ${viewBtn}
                    ${ackBtn}
                </td>
            `;
            myComplianceTbody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        myComplianceTbody.innerHTML = `<tr><td colspan="5">Lỗi tải danh sách policy</td></tr>`;
    }
}

async function acknowledgePolicy(policyId) {
    await apiPost(`/compliance/policies/${policyId}/acknowledge`, {});
    await loadCompliance();

    // nếu đang mở modal thì refresh nội dung + ẩn nút ack
    const updated = compliancePolicyMap.get(Number(policyId));
    if (updated && currentPolicyId === Number(policyId)) {
        openComplianceModal(updated);
    }
}

if (myComplianceTbody) {
    myComplianceTbody.addEventListener("click", async (e) => {
        const btn = e.target.closest("button[data-action]");
        if (!btn) return;

        const id = Number(btn.getAttribute("data-id"));
        const action = btn.getAttribute("data-action");

        if (action === "view") {
            const policy = compliancePolicyMap.get(id);
            if (policy) openComplianceModal(policy);
            return;
        }

        if (action === "ack") {
            try {
                await acknowledgePolicy(id);
                alert("Okela, bạn đã xác nhận policy này rồi nha.");
            } catch (err) {
                console.error(err);
                alert("Lỗi xác nhận policy: " + err.message);
            }
        }
    });
}

// nút ack trong modal
if (compModalAckBtn) {
    compModalAckBtn.addEventListener("click", async () => {
        if (!currentPolicyId) return;
        try {
            await acknowledgePolicy(currentPolicyId);
            alert("Okela, xác nhận xong!");
        } catch (err) {
            console.error(err);
            alert("Lỗi xác nhận policy: " + err.message);
        }
    });
}


// ================= EMPLOYEE ATTENDANCE HEATMAP =================


function initHeatmapDate() {
    const now = new Date();
    myHeatmapYear.value = now.getFullYear();
    myHeatmapMonth.value = now.getMonth() + 1;
}

async function loadEmployeeHeatmap() {
    const year = myHeatmapYear.value;
    const month = myHeatmapMonth.value;
    const wrap = document.getElementById("myAttendanceHeatmap");

    const data = await apiGet(
        `/stats/my-attendance-calendar?year=${year}&month=${month}`
    );

    wrap.innerHTML = "";
    const grid = document.createElement("div");
    grid.className = "heatmap-grid";

    const firstDay = new Date(year, month - 1, 1).getDay();
    const pad = firstDay === 0 ? 6 : firstDay - 1;
    for (let i = 0; i < pad; i++) {
        const e = document.createElement("div");
        e.className = "heatmap-cell empty";
        grid.appendChild(e);
    }

    data.days.forEach(d => {
        const cell = document.createElement("div");
        cell.className = `heatmap-cell ${d.status}`;

        // tooltip
        const tooltip = document.createElement("div");
        tooltip.className = "heatmap-tooltip";

        const labelMap = {
            present: "Đi làm",
            paid_leave: "Nghỉ có phép",
            absent_unexcused: "Nghỉ không phép",
            weekend: "Cuối tuần",
            future: "Tương lai"
        };

        tooltip.textContent = `Ngày ${d.day} – ${labelMap[d.status] || d.status}`;
        cell.appendChild(tooltip);

        grid.appendChild(cell);

    });

    wrap.appendChild(grid);
}

myHeatmapFilterForm.addEventListener("submit", e => {
    e.preventDefault();
    loadEmployeeHeatmap();
});

// auto load khi mở tab attendance
const oldShowView = showView;
showView = function(name) {
    oldShowView(name);
    if (name === "attendance") {
        initHeatmapDate();
        loadEmployeeHeatmap();
    }
};


// ====== INIT ======
showView("profile");
