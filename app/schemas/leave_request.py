from datetime import date, datetime
from typing import Optional, Literal

from pydantic import BaseModel, field_validator


class LeaveBase(BaseModel):
    employee_id: int
    start_date: date
    end_date: date
    reason: Optional[str] = None

    @field_validator("end_date")
    @classmethod
    def check_date_range(cls, v, info):
        # đảm bảo end_date >= start_date
        start = info.data.get("start_date")
        if start and v < start:
            raise ValueError("end_date must be greater than or equal to start_date")
        return v


class LeaveCreate(LeaveBase):
    pass


class LeaveUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = None
    status: Optional[Literal["pending", "approved", "rejected"]] = None


class LeaveOut(LeaveBase):
    id: int
    status: Literal["pending", "approved", "rejected"]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
