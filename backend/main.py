from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, SurveyResponse, User
from schemas import SurveyRequest, UserCreate, UserLogin, UpdatePassword

import pandas as pd
import numpy as np
import os
import io
import csv

# Khởi tạo database
Base.metadata.create_all(bind=engine)

# Khởi tạo ứng dụng FastAPI
app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # hoặc thay "*" bằng ["http://127.0.0.1:5500"] nếu muốn
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------------------------------
# Hàm nạp dữ liệu user từ file Excel
def save_users_to_db(db: Session):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "data_user", "user_df.xlsx")

    df_users = pd.read_excel(file_path)
    # Tạo mật khẩu ngẫu nhiên 6 chữ số
    df_users["password"] = np.random.randint(100000, 999999, size=len(df_users)).astype(str)

    # Tạo user admin nếu chưa có
    admin_user = {
        "username": "admin",
        "password": str(np.random.randint(100000, 999999)),
        "role": "admin",
        "branch_id": "000"
    }

    for _, row in df_users.iterrows():
        # Kiểm tra user đã tồn tại chưa
        existing_user = db.query(User).filter(User.username == row["User"]).first()
        if not existing_user:
            # Tạo mới user
            user = User(
                username=row["User"],
                password=row["password"],
                role="user",
                branch_id=str(row["Mã Đơn vị"]),
                position=row["Chức vụ"]  # Lưu chức danh vào cột position
            )
            db.add(user)

    # Kiểm tra admin
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if not existing_admin:
        db.add(User(**admin_user))

    db.commit()


# Chạy hàm lưu user khi khởi động
with SessionLocal() as db:
    save_users_to_db(db)


# -----------------------------------------------------
# API đăng nhập
@app.post("/login/")
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Nhận username, password -> Kiểm tra user trong DB.
    Trả về {message, role, username, branch_id}.
    """
    user = db.query(User).filter(User.username == user_data.username,
                                 User.password == user_data.password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu")
    
    return {
        "message": "Đăng nhập thành công",
        "role": user.role,
        "username": user.username,
        "branch_id": user.branch_id
    }


# -----------------------------------------------------
# API gửi khảo sát
@app.post("/submit_survey/")
def submit_survey(survey: SurveyRequest, db: Session = Depends(get_db)):
    """
    Lưu dữ liệu khảo sát vào bảng survey_responses.
    Đồng thời nếu survey.username có gửi -> đánh dấu user đó đã nộp (survey_submitted = True).
    """
    # 1) Lưu form khảo sát
    survey_data = SurveyResponse(
        branch_id=survey.branch_id,
        csvc=", ".join(survey.csvc) if survey.csvc else "",
        csqd=", ".join(survey.csqd) if survey.csqd else "",
        hotro=", ".join(survey.hotro) if survey.hotro else "",
        proposal=survey.proposal,
        pgd_info=survey.pgd_info,
        other_pgd=survey.other_pgd,
        additional_comments=survey.additional_comments
    )
    db.add(survey_data)
    db.commit()
    db.refresh(survey_data)

    # 2) Nếu có username -> đánh dấu user.survey_submitted = True
    if survey.username:
        user = db.query(User).filter(User.username == survey.username).first()
        if user:
            user.survey_submitted = True
            db.commit()

    return {"message": "Khảo sát đã được gửi thành công!", "data": survey_data}


# -----------------------------------------------------
# API cập nhật mật khẩu
@app.put("/update_password/")
def update_password(user_data: UpdatePassword, db: Session = Depends(get_db), admin_user: str = "admin"):
    """
    Chỉ admin mới được đổi mật khẩu user khác.
    """
    # Kiểm tra admin
    admin = db.query(User).filter(User.username == admin_user, User.role == "admin").first()
    if not admin:
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền cập nhật mật khẩu")

    # Tìm user cần đổi pass
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")

    # Đổi pass
    user.password = user_data.new_password
    db.commit()
    return {"message": f"Mật khẩu của {user_data.username} đã được cập nhật thành công"}


# -----------------------------------------------------
# API xuất CSV
@app.get("/export_survey_csv/")
def export_survey_csv(db: Session = Depends(get_db)):
    """Xuất toàn bộ survey_responses dưới dạng CSV."""
    surveys = db.query(SurveyResponse).all()
    
    headers = ["id", "branch_id", "csvc", "csqd", "hotro", "proposal",
               "pgd_info", "other_pgd", "additional_comments"]
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(headers)
    for s in surveys:
        writer.writerow([
            s.id,
            s.branch_id,
            s.csvc,
            s.csqd,
            s.hotro,
            s.proposal,
            s.pgd_info,
            s.other_pgd,
            s.additional_comments
        ])
    
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=survey_data.csv"}
    )


# -----------------------------------------------------
# API thống kê khảo sát
@app.get("/survey_stats/")
def survey_stats(db: Session = Depends(get_db)):
    """Thống kê số lần các lựa chọn CSV, CSQD, HOTRO được tick."""
    surveys = db.query(SurveyResponse).all()

    csvc_counts = {}
    csqd_counts = {}
    hotro_counts = {}

    for s in surveys:
        # csvc
        if s.csvc:
            items = s.csvc.split(",")
            for item in items:
                item = item.strip()
                csvc_counts[item] = csvc_counts.get(item, 0) + 1

        # csqd
        if s.csqd:
            items = s.csqd.split(",")
            for item in items:
                item = item.strip()
                csqd_counts[item] = csqd_counts.get(item, 0) + 1

        # hotro
        if s.hotro:
            items = s.hotro.split(",")
            for item in items:
                item = item.strip()
                hotro_counts[item] = hotro_counts.get(item, 0) + 1

    return {
        "csvc_counts": csvc_counts,
        "csqd_counts": csqd_counts,
        "hotro_counts": hotro_counts,
        "total_surveys": len(surveys)
    }


# -----------------------------------------------------
# API xem user đã / chưa nộp
@app.get("/user_survey_status/")
def user_survey_status(db: Session = Depends(get_db)):
    """
    Dựa vào user.survey_submitted:
    done[] = list user đã nộp, not_done[] = list user chưa nộp
    """
    users = db.query(User).all()
    done = []
    not_done = []
    for u in users:
        if u.survey_submitted:
            done.append(u.username)
        else:
            not_done.append(u.username)
    return {"done": done, "not_done": not_done}

