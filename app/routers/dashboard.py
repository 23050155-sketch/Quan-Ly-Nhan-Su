from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave_request import LeaveRequest
from app.models.payroll import Payroll

from app.core.security import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview")
def dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    today = date.today()
    year = today.year
    month = today.month

    # 1. Tổng nhân viên
    total_employees = db.query(func.count(Employee.id)).scalar() or 0

    # 2. Nhân viên đã chấm công hôm nay
    today_attendance = (
        db.query(Attendance.employee_id)
        .filter(
            Attendance.date == today,
            Attendance.check_in.isnot(None)
        )
        .distinct()
        .count()
    )

    # 3. Đơn nghỉ chờ duyệt
    pending_leaves = (
        db.query(func.count(LeaveRequest.id))
        .filter(LeaveRequest.status == "pending")
        .scalar() or 0
    )

    # 4. Tổng quỹ lương tháng hiện tại
    total_salary = (
        db.query(func.coalesce(func.sum(Payroll.net_salary), 0))
        .filter(
            Payroll.year == year,
            Payroll.month == month
        )
        .scalar() or 0
    )

    return {
        "total_employees": total_employees,
        "today_attendance": today_attendance,
        "pending_leaves": pending_leaves,
        "current_month_total_salary": float(total_salary)
    }
