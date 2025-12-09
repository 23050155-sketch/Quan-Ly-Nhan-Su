const form = document.getElementById("loginForm");
const errorBox = document.getElementById("errorBox");
const successBox = document.getElementById("successBox");
const loginBtn = document.getElementById("loginBtn");
const btnText = document.getElementById("btnText");
const btnLoader = document.getElementById("btnLoader");

function setLoading(isLoading) {
    if (isLoading) {
        loginBtn.disabled = true;
        btnText.textContent = "Đang đăng nhập...";
        btnLoader.style.display = "inline-block";
    } else {
        loginBtn.disabled = false;
        btnText.textContent = "Đăng nhập";
        btnLoader.style.display = "none";
    }
}

function showError(msg) {
    if (!msg) {
        errorBox.style.display = "none";
        return;
    }
    errorBox.textContent = msg;
    errorBox.style.display = "block";
    successBox.style.display = "none";
}

function showSuccess(msg) {
    successBox.textContent = msg;
    successBox.style.display = "block";
    errorBox.style.display = "none";
}

async function login(username, password) {
    const body = new URLSearchParams();
    body.append("username", username);
    body.append("password", password);

    const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body
    });

    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Đăng nhập thất bại");
    }

    return res.json(); // { access_token, token_type }
}

async function fetchMe(token) {
    const res = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Không lấy được thông tin người dùng");
    }

    return res.json(); // UserOut
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (!username || !password) {
        showError("Vui lòng nhập đầy đủ username và password.");
        return;
    }

    setLoading(true);
    showError("");
    successBox.style.display = "none";

    try {
        // 1. login → lấy token
        const tokenRes = await login(username, password);
        const accessToken = tokenRes.access_token;

        // 2. lưu token
        localStorage.setItem(TOKEN_KEY, accessToken);

        // 3. lấy info user
        const me = await fetchMe(accessToken);

        // 4. lưu info lại
        localStorage.setItem(USER_INFO_KEY, JSON.stringify(me));

        showSuccess("Đăng nhập thành công! Đang chuyển hướng...");

        // 5. redirect theo role
        if (me.role === "admin") {
            window.location.href = ADMIN_DASHBOARD_URL;
        } else {
            window.location.href = EMPLOYEE_HOME_URL;
        }
    } catch (err) {
        console.error(err);
        showError("Sai username/password hoặc có lỗi khi đăng nhập.");
    } finally {
        setLoading(false);
    }
});

// auto redirect nếu đã login sẵn
(async function autoRedirectIfLoggedIn() {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) return;

    try {
        const me = await fetchMe(token);
        if (me && me.role) {
            if (me.role === "admin") {
                window.location.href = ADMIN_DASHBOARD_URL;
            } else {
                window.location.href = EMPLOYEE_HOME_URL;
            }
        }
    } catch (e) {
        console.log("Token không hợp lệ, yêu cầu login lại.");
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_INFO_KEY);
    }
})();
