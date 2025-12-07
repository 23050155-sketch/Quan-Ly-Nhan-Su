from calendar import monthrange
from datetime import date
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave_request import LeaveRequest
from app.models.payroll import Payroll
from app.schemas.stats import (
    OverviewStats,
    AttendanceSummary,
    AttendanceSummaryItem,
    LeaveSummary,
    LeaveSummaryItem,
)

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/overview", response_model=OverviewStats)
def get_overview_stats(db: Session = Depends(get_db)):
    today = date.today()
    year = today.year
    month = today.month

    # tổng nhân viên
    total_employees = db.query(func.count(Employee.id)).scalar() or 0

    # số nhân viên đã chấm công hôm nay
    todays_attendance_count = (
        db.query(Attendance.employee_id)
        .filter(Attendance.date == today, Attendance.check_in.isnot(None))
        .distinct()
        .count()
    )

    # số đơn nghỉ đang pending
    pending_leave_requests = (
        db.query(func.count(LeaveRequest.id))
        .filter(LeaveRequest.status == "pending")
        .scalar()
        or 0
    )

    # tổng lương tháng hiện tại (net_salary)
    current_month_total_payroll = (
        db.query(func.coalesce(func.sum(Payroll.net_salary), 0.0))
        .filter(Payroll.year == year, Payroll.month == month)
        .scalar()
        or 0.0
    )

    return OverviewStats(
        total_employees=total_employees,
        todays_attendance_count=todays_attendance_count,
        pending_leave_requests=pending_leave_requests,
        current_month_total_payroll=float(current_month_total_payroll),
    )


@router.get("/attendance-summary", response_model=AttendanceSummary)
def get_attendance_summary(year: int, month: int, db: Session = Depends(get_db)):
    start_month = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_month = date(year, month, last_day)

    rows = (
        db.query(
            Attendance.employee_id,
            func.count(func.distinct(Attendance.date)).label("days"),
        )
        .filter(
            Attendance.date >= start_month,
            Attendance.date <= end_month,
            Attendance.check_in.isnot(None),
        )
        .group_by(Attendance.employee_id)
        .all()
    )

    items = [
        AttendanceSummaryItem(employee_id=row.employee_id, days=row.days)
        for row in rows
    ]

    return AttendanceSummary(year=year, month=month, items=items)


@router.get("/leave-summary", response_model=LeaveSummary)
def get_leave_summary(year: int, month: int, db: Session = Depends(get_db)):
    start_month = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_month = date(year, month, last_day)

    # lấy các đơn đã approved có giao với khoảng [start_month, end_month]
    rows = (
        db.query(
            LeaveRequest.employee_id,
            LeaveRequest.start_date,
            LeaveRequest.end_date,
        )
        .filter(
            LeaveRequest.status == "approved",
            LeaveRequest.start_date <= end_month,
            LeaveRequest.end_date >= start_month,
        )
        .all()
    )

    # tính số ngày nghỉ theo từng nhân viên
    days_by_emp = {}
    for emp_id, start, end in rows:
        s = max(start, start_month)
        e = min(end, end_month)
        days = (e - s).days + 1
        days_by_emp[emp_id] = days_by_emp.get(emp_id, 0) + days

    items = [
        LeaveSummaryItem(employee_id=emp_id, days=days)
        for emp_id, days in days_by_emp.items()
    ]

    return LeaveSummary(year=year, month=month, items=items)
