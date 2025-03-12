document.addEventListener("DOMContentLoaded", function() {
    // 1) Kiểm tra đăng nhập
    const username = localStorage.getItem("username");
    const branch_id = localStorage.getItem("branch_id");

    if (!username || !branch_id) {
        window.location.href = "login.html";
        return;
    }

    // 2) Hiển thị lên giao diện
    document.getElementById("username").textContent = username;
    document.getElementById("branch_id").textContent = branch_id;

    // 3) Nút logout
    const logoutBtn = document.getElementById("logout-btn");
    logoutBtn.addEventListener("click", function() {
        localStorage.clear();
        window.location.href = "login.html";
    });

    // 4) Xử lý form khảo sát
    const surveyForm = document.getElementById("surveyForm");
    surveyForm.addEventListener("submit", async function(event) {
        event.preventDefault(); // Ngăn form reload

        const formData = new FormData(surveyForm);
        const csvc = formData.getAll("csvc");
        const csqd = formData.getAll("csqd");
        const hotro = formData.getAll("hotro");
        const proposal = formData.get("proposal") || "";
        const pgd_info = formData.get("pgd_info") || "";
        const other_pgd = formData.get("other_pgd") || "";
        const additional_comments = formData.get("additional_comments") || "";

        const payload = {
            branch_id: branch_id,
            csvc: csvc,
            csqd: csqd,
            hotro: hotro,
            proposal: proposal,
            pgd_info: pgd_info,
            other_pgd: other_pgd,
            additional_comments: additional_comments
        };

        try {
            const response = await fetch("http://127.0.0.1:8000/submit_survey/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const result = await response.json();

            if (response.ok) {
                alert("Gửi khảo sát thành công!");
            } else {
                alert("Lỗi: " + (result.detail || "Không thể gửi khảo sát."));
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Lỗi kết nối máy chủ!");
        }
    });
});

