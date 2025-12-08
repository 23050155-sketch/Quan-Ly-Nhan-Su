from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.database import get_db
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceOut,
)

from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/attendances", tags=["Attendance"])


# ✅ Tạo bản ghi chấm công
@router.post("/", response_model=AttendanceOut)
def create_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin" and current_user.employee_id != data.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không được phép chấm công cho nhân viên khác",
        )

    emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên")

    existed = (
        db.query(Attendance)
        .filter(
            Attendance.employee_id == data.employee_id,
            Attendance.date == data.date,
        )
        .first()
    )
    if existed:
        raise HTTPException(
            status_code=400,
            detail="Nhân viên đã được chấm công cho ngày này rồi",
        )

    att = Attendance(**data.dict())
    db.add(att)
    db.commit()
    db.refresh(att)
    return att


# ✅ Lấy danh sách chấm công
@router.get("/", response_model=List[AttendanceOut])
def get_attendances(
    employee_id: int | None = None,
    work_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Attendance)

    # ❌ User thường: CHỈ được xem chấm công của chính mình
    if current_user.role != "admin":
        if employee_id is not None and employee_id != current_user.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không được phép xem chấm công của nhân viên khác",
            )
        query = query.filter(Attendance.employee_id == current_user.employee_id)

    # ✅ Admin: được xem / filter theo bất kỳ employee_id nào
    else:
        if employee_id is not None:
            query = query.filter(Attendance.employee_id == employee_id)

    if work_date is not None:
        query = query.filter(Attendance.date == work_date)

    return query.all()


# ✅ Lấy 1 bản ghi chấm công
@router.get("/{att_id}", response_model=AttendanceOut)
def get_attendance(
    att_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    att = db.query(Attendance).filter(Attendance.id == att_id).first()
    if not att:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi chấm công")

    if current_user.role != "admin" and current_user.employee_id != att.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không được phép xem chấm công của người khác",
        )

    return att


# ✅ Cập nhật giờ check-in / check-out
@router.put("/{att_id}", response_model=AttendanceOut)
def update_attendance(
    att_id: int,
    data: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    att = db.query(Attendance).filter(Attendance.id == att_id).first()
    if not att:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi chấm công")

    if current_user.role != "admin" and current_user.employee_id != att.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không được phép sửa chấm công của người khác",
        )

    for key, value in data.dict(exclude_unset=True).items():
        setattr(att, key, value)

    db.commit()
    db.refresh(att)
    return att


# ✅ Xoá bản ghi chấm công (chỉ admin)
@router.delete("/{att_id}")
def delete_attendance(
    att_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ quản trị viên mới được phép xoá bản ghi chấm công",
        )

    att = db.query(Attendance).filter(Attendance.id == att_id).first()
    if not att:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi chấm công")

    db.delete(att)
    db.commit()
    return {"message": "Xoá bản ghi chấm công thành công"}
