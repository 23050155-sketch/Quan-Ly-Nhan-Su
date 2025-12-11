from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# ====== USER BASE ======
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    role: str = "employee"        # admin / employee
    employee_id: Optional[int] = None


# ====== CREATE USER ======
class UserCreate(UserBase):
    password: str                 # mật khẩu plain để hash


# ====== UPDATE USER ======
class UserUpdate(UserBase):
    password: Optional[str] = None   # cho phép bỏ trống khi update


# ====== USER OUTPUT ======
class UserOut(UserBase):
    id: int
    created_at: Optional[datetime] = None   

    class Config:
        orm_mode = True


# ====== TOKEN ======
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
