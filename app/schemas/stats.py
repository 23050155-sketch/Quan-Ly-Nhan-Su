from pydantic import BaseModel
from typing import List
from datetime import date


class OverviewStats(BaseModel):
    total_employees: int
    todays_attendance_count: int
    pending_leave_requests: int
    current_month_total_payroll: float


class AttendanceSummaryItem(BaseModel):
    employee_id: int
    days: int


class AttendanceSummary(BaseModel):
    year: int
    month: int
    items: List[AttendanceSummaryItem]


class LeaveSummaryItem(BaseModel):
    employee_id: int
    days: int


class LeaveSummary(BaseModel):
    year: int
    month: int
    items: List[LeaveSummaryItem]
