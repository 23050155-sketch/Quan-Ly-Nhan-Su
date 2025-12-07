from fastapi import APIRouter, Depends, HTTPException
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

router = APIRouter(prefix="/attendances", tags=["Attendance"])


# ✅ Tạo bản ghi chấm công (check-in + check-out cùng lúc hoặc chỉ check-in)
@router.post("/", response_model=AttendanceOut)
def create_attendance(data: AttendanceCreate, db: Session = Depends(get_db)):
    # check nhân viên có tồn tại không
    emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # kiểm tra đã có bản ghi ngày đó chưa (tránh trùng)
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
            status_code=400, detail="Attendance for this date already exists"
        )

    att = Attendance(**data.dict())
    db.add(att)
    db.commit()
    db.refresh(att)
    return att


# ✅ Lấy danh sách chấm công (có filter theo employee_id & date optional)
@router.get("/", response_model=List[AttendanceOut])
def get_attendances(
    employee_id: int | None = None,
    work_date: date | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Attendance)
    if employee_id is not None:
        query = query.filter(Attendance.employee_id == employee_id)
    if work_date is not None:
        query = query.filter(Attendance.date == work_date)
    return query.all()


# ✅ Lấy 1 bản ghi chấm công
@router.get("/{att_id}", response_model=AttendanceOut)
def get_attendance(att_id: int, db: Session = Depends(get_db)):
    att = db.query(Attendance).filter(Attendance.id == att_id).first()
    if not att:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return att


# ✅ Update giờ check-in / check-out
@router.put("/{att_id}", response_model=AttendanceOut)
def update_attendance(
    att_id: int,
    data: AttendanceUpdate,
    db: Session = Depends(get_db),
):
    att = db.query(Attendance).filter(Attendance.id == att_id).first()
    if not att:
        raise HTTPException(status_code=404, detail="Attendance not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(att, key, value)

    db.commit()
    db.refresh(att)
    return att


# ✅ Xoá bản ghi chấm công
@router.delete("/{att_id}")
def delete_attendance(att_id: int, db: Session = Depends(get_db)):
    att = db.query(Attendance).filter(Attendance.id == att_id).first()
    if not att:
        raise HTTPException(status_code=404, detail="Attendance not found")

    db.delete(att)
    db.commit()
    return {"message": "Attendance deleted successfully"}
