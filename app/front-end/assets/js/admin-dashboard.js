const token = localStorage.getItem(TOKEN_KEY);
const userInfo = JSON.parse(localStorage.getItem(USER_INFO_KEY) || "{}");

if (!token) {
    // Chưa login → đá về login
    window.location.href = "/html/login.html";
}

// Hiển thị tên admin (nếu có)
document.getElementById("adminName").textContent =
    userInfo.username || "Admin";

// Check quyền & load stats
async function loadDashboard() {
    // Check role
    if (userInfo.role !== "admin") {
        alert("Bạn không có quyền truy cập trang admin!");
        window.location.href = "/html/login.html";
        return;
    }

    const res = await fetch(`${API_BASE_URL}/stats/overview`, {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (!res.ok) {
        alert("Không tải được dữ liệu dashboard!");
        return;
    }

    const data = await res.json();

    document.getElementById("totalEmployees").textContent =
        data.total_employees;

    document.getElementById("todayAttendance").textContent =
        data.todays_attendance_count;

    document.getElementById("pendingLeaves").textContent =
        data.pending_leave_requests;

    document.getElementById("totalSalary").textContent =
        data.current_month_total_payroll.toLocaleString("vi-VN") + " đ";
}

// Logout
document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.clear();
    window.location.href = "/html/login.html";
});

// Load khi mở trang
loadDashboard();
