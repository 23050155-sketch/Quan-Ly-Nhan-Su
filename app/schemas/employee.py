from pydantic import BaseModel
from datetime import date
from typing import Optional

class EmployeeBase(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    position: Optional[str] = None
    department: Optional[str] = None
    start_date: Optional[date] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass

class EmployeeOut(EmployeeBase):
    id: int

    class Config:
        from_attributes = True
