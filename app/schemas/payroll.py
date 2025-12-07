from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional


class PayrollBase(BaseModel):
    employee_id: int
    year: int
    month: int
    base_daily_salary: float
    deductions: float = 0.0

    @field_validator("month")
    @classmethod
    def check_month(cls, v):
        if v < 1 or v > 12:
            raise ValueError("month must be between 1 and 12")
        return v


class PayrollCreate(PayrollBase):
    pass


class PayrollOut(BaseModel):
    id: int
    employee_id: int
    year: int
    month: int
    base_daily_salary: float
    attendance_days: int
    paid_leave_days: int
    gross_salary: float
    deductions: float
    net_salary: float
    created_at: datetime

    class Config:
        from_attributes = True
