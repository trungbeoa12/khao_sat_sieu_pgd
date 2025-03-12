document.getElementById("login-form").addEventListener("submit", async function(event) {
    event.preventDefault();

    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    let loginData = {
        "username": username,
        "password": password,
        "role": "user",
        "branch_id": "106"
    };

    try {
        let response = await fetch("http://127.0.0.1:8000/login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(loginData)
        });

        let result = await response.json();

        if (response.status === 200) {
            // Lưu thông tin user vào localStorage
            localStorage.setItem("username", username);
            localStorage.setItem("role", result.role);
            localStorage.setItem("branch_id", result.branch_id || "Không có chi nhánh");

            // Chuyển hướng theo vai trò
            if (result.role === "admin") {
                window.location.href = "admin_dashboard.html";  // Nếu có trang quản trị
            } else {
                window.location.href = "survey.html";
            }
        } else {
            document.getElementById("login-message").innerHTML = `<span style="color: red;">${result.detail}</span>`;
        }
    } catch (error) {
        console.error("Lỗi kết nối:", error);
        document.getElementById("login-message").innerHTML = `<span style="color: red;">Lỗi máy chủ!</span>`;
    }
});

document.addEventListener("DOMContentLoaded", function() {
    // Lấy thông tin user từ localStorage
    const username = localStorage.getItem("username");
    const branch_id = localStorage.getItem("branch_id");

    // Hiển thị tên người dùng trên giao diện
    if (username) {
        document.getElementById("username-display").innerText = username;
        document.getElementById("branch_id").innerText = branch_id || "Không có chi nhánh";
    }

    // Xử lý khi click vào nút Logout
    document.getElementById("logout-btn").addEventListener("click", function() {
        localStorage.clear(); // Xóa dữ liệu đăng nhập
        window.location.href = "login.html"; // Chuyển về trang đăng nhập
    });
});

