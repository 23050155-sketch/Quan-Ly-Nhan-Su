from calendar import monthrange
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave_request import LeaveRequest
from app.models.payroll import Payroll
from app.schemas.payroll import PayrollCreate, PayrollOut

router = APIRouter(prefix="/payrolls", tags=["Payroll"])


def _calc_paid_leave_days(
    employee_id: int, year: int, month: int, db: Session
) -> int:
    """Tính số ngày nghỉ có phép (approved) trong tháng"""
    start_month = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_month = date(year, month, last_day)

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

    total_days = 0
    for lv in leaves:
        s = max(lv.start_date, start_month)
        e = min(lv.end_date, end_month)
        total_days += (e - s).days + 1
    return total_days


def _calc_attendance_days(
    employee_id: int, year: int, month: int, db: Session
) -> int:
    """Tính số ngày đi làm (có check_in) trong tháng"""
    start_month = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_month = date(year, month, last_day)

    q = (
        db.query(Attendance.date)
        .filter(
            Attendance.employee_id == employee_id,
            Attendance.date >= start_month,
            Attendance.date <= end_month,
            Attendance.check_in.isnot(None),
        )
        .distinct()
    )

    return q.count()


# ✅ Tính lương và lưu Payroll
@router.post("/calculate", response_model=PayrollOut)
def calculate_payroll(data: PayrollCreate, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # check đã có bảng lương tháng này chưa
    existed = (
        db.query(Payroll)
        .filter(
            Payroll.employee_id == data.employee_id,
            Payroll.year == data.year,
            Payroll.month == data.month,
        )
        .first()
    )
    if existed:
        raise HTTPException(
            status_code=400,
            detail="Payroll for this employee and month already exists",
        )

    attendance_days = _calc_attendance_days(
        data.employee_id, data.year, data.month, db
    )
    paid_leave_days = _calc_paid_leave_days(
        data.employee_id, data.year, data.month, db
    )

    gross_salary = data.base_daily_salary * (
        attendance_days + paid_leave_days
    )
    net_salary = gross_salary - data.deductions

    payroll = Payroll(
        employee_id=data.employee_id,
        year=data.year,
        month=data.month,
        base_daily_salary=data.base_daily_salary,
        attendance_days=attendance_days,
        paid_leave_days=paid_leave_days,
        gross_salary=gross_salary,
        deductions=data.deductions,
        net_salary=net_salary,
    )

    db.add(payroll)
    db.commit()
    db.refresh(payroll)
    return payroll


# ✅ Lấy danh sách bảng lương (có filter)
@router.get("/", response_model=List[PayrollOut])
def list_payrolls(
    employee_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Payroll)
    if employee_id is not None:
        q = q.filter(Payroll.employee_id == employee_id)
    if year is not None:
        q = q.filter(Payroll.year == year)
    if month is not None:
        q = q.filter(Payroll.month == month)
    return q.all()


# ✅ Lấy 1 payroll theo id
@router.get("/{payroll_id}", response_model=PayrollOut)
def get_payroll(payroll_id: int, db: Session = Depends(get_db)):
    p = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Payroll not found")
    return p
