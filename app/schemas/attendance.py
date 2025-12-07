from pydantic import BaseModel
from datetime import date, time
from typing import Optional


class AttendanceBase(BaseModel):
    employee_id: int
    date: date
    check_in: Optional[time] = None
    check_out: Optional[time] = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    check_in: Optional[time] = None
    check_out: Optional[time] = None


class AttendanceOut(AttendanceBase):
    id: int

    class Config:
        from_attributes = True
