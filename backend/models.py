from sqlalchemy import Column, Integer, String, Text, Boolean
from database import Base

# Định nghĩa bảng lưu trữ khảo sát
class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(String, index=True)
    csvc = Column(Text)
    csqd = Column(Text)
    hotro = Column(Text)
    proposal = Column(String)
    pgd_info = Column(String, nullable=True)
    other_pgd = Column(Text, nullable=True)
    additional_comments = Column(Text, nullable=True)

# Định nghĩa bảng User
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # Mật khẩu sẽ được mã hóa trong thực tế
    role = Column(String, default="user")  # user hoặc admin
    branch_id = Column(String, nullable=True)
    survey_submitted = Column(Boolean, default=False)
    position = Column(String, nullable=True)  # cột Chức vụ

