from calendar import monthrange
from datetime import date
from typing import List

from datetime import timedelta
from app.schemas.stats import AttendanceHeatmap, AttendanceHeatmapDay

from fastapi import APIRouter, Depends, HTTPException, status
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

from app.core.security import get_current_admin, get_current_user
from app.models.user import User

router = APIRouter(prefix="/stats", tags=["Statistics"])


# ✅ Tổng quan hệ thống – CHỈ ADMIN
@router.get("/overview", response_model=OverviewStats)
def get_overview_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
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


# ✅ Tổng hợp chấm công theo tháng – CHỈ ADMIN
@router.get("/attendance-summary", response_model=AttendanceSummary)
def get_attendance_summary(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
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


# ✅ Tổng hợp ngày nghỉ có phép theo tháng – CHỈ ADMIN
@router.get("/leave-summary", response_model=LeaveSummary)
def get_leave_summary(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    start_month = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_month = date(year, month, last_day)

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


@router.get("/attendance-heatmap", response_model=AttendanceHeatmap)
def get_attendance_heatmap(
    employee_id: int,
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    # validate employee
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên")

    start_month = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_month = date(year, month, last_day)

    # 1) attendance days (có check_in)
    att_rows = (
        db.query(Attendance.date)
        .filter(
            Attendance.employee_id == employee_id,
            Attendance.date >= start_month,
            Attendance.date <= end_month,
            Attendance.check_in.isnot(None),
        )
        .all()
    )
    present_days = {r[0] for r in att_rows}

    # 2) paid leave days (approved, overlap month)
    leaves = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.status == "approved",
            LeaveRequest.start_date <= end_month,
            LeaveRequest.end_date >= start_month,
        )
        .all()
    )

    paid_leave_days = set()
    for lv in leaves:
        s = max(lv.start_date, start_month)
        e = min(lv.end_date, end_month)
        d = s
        while d <= e:
            paid_leave_days.add(d)
            d += timedelta(days=1)

    # 3) build days
    today = date.today()
    out_days = []

    d = start_month
    while d <= end_month:
        # weekend: Saturday(5) Sunday(6)
        is_weekend = d.weekday() in (5, 6)

        if d in present_days:
            status_str = "present"
        elif d in paid_leave_days:
            status_str = "paid_leave"
        else:
            if d > today:
                status_str = "future"
            else:
                status_str = "weekend" if is_weekend else "absent_unexcused"

        out_days.append(AttendanceHeatmapDay(date=d, status=status_str))
        d += timedelta(days=1)

    return AttendanceHeatmap(
        employee_id=employee_id,
        year=year,
        month=month,
        days=out_days
    )
    
    
    
@router.get("/my-attendance-calendar")
def my_attendance_calendar(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # đảm bảo user có employee_id
    if not current_user.employee_id:
        raise HTTPException(
            status_code=400,
            detail="Tài khoản chưa gắn với nhân viên"
        )

    employee_id = current_user.employee_id

    start_month = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_month = date(year, month, last_day)

    # 1️⃣ attendance days
    att_rows = (
        db.query(Attendance.date)
        .filter(
            Attendance.employee_id == employee_id,
            Attendance.date >= start_month,
            Attendance.date <= end_month,
            Attendance.check_in.isnot(None),
        )
        .all()
    )
    present_days = {r[0] for r in att_rows}

    # 2️⃣ paid leave days
    leaves = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.status == "approved",
            LeaveRequest.start_date <= end_month,
            LeaveRequest.end_date >= start_month,
        )
        .all()
    )

    paid_leave_days = set()
    for lv in leaves:
        s = max(lv.start_date, start_month)
        e = min(lv.end_date, end_month)
        d = s
        while d <= e:
            paid_leave_days.add(d)
            d += timedelta(days=1)

    # 3️⃣ build days
    today = date.today()
    days = []
    d = start_month
    while d <= end_month:
        if d in present_days:
            status = "present"
        elif d in paid_leave_days:
            status = "paid_leave"
        elif d.weekday() in (5, 6):
            status = "weekend"
        elif d > today:
            status = "future"
        else:
            status = "absent_unexcused"

        days.append({
            "day": d.day,
            "status": status
        })
        d += timedelta(days=1)

    return {
        "year": year,
        "month": month,
        "days": days
    }
