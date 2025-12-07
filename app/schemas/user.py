from typing import Optional, Literal
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    role: Literal["admin", "employee"] = "employee"
    employee_id: Optional[int] = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
