document.addEventListener("DOMContentLoaded", function() {
    // Tìm form đăng nhập
    const loginForm = document.getElementById("login-form");
    // Nếu trang login không có form này, code sẽ không làm gì
    if (!loginForm) return;

    loginForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        let username = document.getElementById("username").value;
        let password = document.getElementById("password").value;

        let loginData = {
            "username": username,
            "password": password
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

            if (response.ok) {
                // Lưu thông tin user
                localStorage.setItem("username", result.username);
                localStorage.setItem("role", result.role);
                localStorage.setItem("branch_id", result.branch_id || "");

                // Chuyển hướng
                if (result.role === "admin") {
                    window.location.href = "admin_dashboard.html";
                } else {
                    window.location.href = "survey.html";
                }
            } else {
                document.getElementById("login-message").innerHTML = 
                    `<span style="color: red;">${result.detail || "Lỗi đăng nhập"}</span>`;
            }
        } catch (error) {
            console.error("Lỗi kết nối:", error);
            document.getElementById("login-message").innerHTML = 
                `<span style="color: red;">Lỗi máy chủ!</span>`;
        }
    });
});

