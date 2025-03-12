from pydantic import BaseModel
from typing import List, Optional

# Định nghĩa cấu trúc dữ liệu API
type_list = List[str] | None  # Python 3.10+

class SurveyRequest(BaseModel):
    branch_id: str
    csvc: type_list
    csqd: type_list
    hotro: type_list
    proposal: str
    pgd_info: Optional[str]
    other_pgd: Optional[str]
    additional_comments: Optional[str]
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str] = None
    branch_id: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str
    
class UpdatePassword(BaseModel):
    username: str
    new_password: str

