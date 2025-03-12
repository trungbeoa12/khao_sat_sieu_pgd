document.addEventListener("DOMContentLoaded", () => {
    // 1) Kiểm tra role admin
    const role = localStorage.getItem("role");
    const username = localStorage.getItem("username");
    if (!username || role !== "admin") {
        // Không phải admin => Quay về đăng nhập
        window.location.href = "login.html";
    }
    // Hiển thị tên admin
    document.getElementById("username-display").innerText = username;

    // 2) Nút Đăng xuất
    const logoutBtn = document.getElementById("logout-btn");
    logoutBtn.addEventListener("click", () => {
        localStorage.clear();
        window.location.href = "login.html";
    });

    // 3) Nút Xuất CSV
    document.getElementById("export-csv-btn").addEventListener("click", () => {
        // Gọi trực tiếp link export CSV
        window.location.href = "http://127.0.0.1:8000/export_survey_csv/";
    });

    // 4) Nút Thống kê
    document.getElementById("stats-btn").addEventListener("click", async () => {
        try {
            const res = await fetch("http://127.0.0.1:8000/survey_stats/");
            const data = await res.json();

            /*
              data = {
                csvc_counts: {...},
                csqd_counts: {...},
                hotro_counts: {...},
                total_surveys: 10
              }
            */

            let html = `<p>Tổng số khảo sát: <b>${data.total_surveys}</b></p>`;

            html += "<h4>CSVc counts:</h4><ul>";
            for (const [key, val] of Object.entries(data.csvc_counts)) {
                html += `<li>${key}: ${val}</li>`;
            }
            html += "</ul>";

            html += "<h4>CSQD counts:</h4><ul>";
            for (const [key, val] of Object.entries(data.csqd_counts)) {
                html += `<li>${key}: ${val}</li>`;
            }
            html += "</ul>";

            html += "<h4>Hỗ trợ counts:</h4><ul>";
            for (const [key, val] of Object.entries(data.hotro_counts)) {
                html += `<li>${key}: ${val}</li>`;
            }
            html += "</ul>";

            document.getElementById("stats-result").innerHTML = html;
        } catch (error) {
            console.error(error);
            alert("Không thể lấy dữ liệu thống kê!");
        }
    });

    // 5) Nút Trạng thái người dùng
    document.getElementById("status-btn").addEventListener("click", async () => {
        try {
            const res = await fetch("http://127.0.0.1:8000/user_survey_status/");
            const data = await res.json();
            /*
                data = {
                  done: ["user1", "user2"],
                  not_done: ["admin", "user3"]
                }
            */
            let html = "<h4>Đã nộp khảo sát:</h4><ul>";
            data.done.forEach(u => {
                html += `<li>${u}</li>`;
            });
            html += "</ul><h4>Chưa nộp khảo sát:</h4><ul>";
            data.not_done.forEach(u => {
                html += `<li>${u}</li>`;
            });
            html += "</ul>";

            document.getElementById("status-result").innerHTML = html;
        } catch (error) {
            console.error(error);
            alert("Không thể lấy trạng thái người dùng!");
        }
    });
});

