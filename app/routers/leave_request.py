from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employee import Employee
from app.models.leave_request import LeaveRequest
from app.schemas.leave_request import (
    LeaveCreate,
    LeaveUpdate,
    LeaveOut,
)

router = APIRouter(prefix="/leaves", tags=["Leave Requests"])


# ✅ Tạo đơn xin nghỉ (mặc định status = pending)
@router.post("/", response_model=LeaveOut)
def create_leave(data: LeaveCreate, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    leave = LeaveRequest(**data.dict())
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave


# ✅ Lấy danh sách đơn (có filter theo employee_id, status, date)
@router.get("/", response_model=List[LeaveOut])
def list_leaves(
    employee_id: Optional[int] = None,
    status: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    q = db.query(LeaveRequest)

    if employee_id is not None:
        q = q.filter(LeaveRequest.employee_id == employee_id)
    if status is not None:
        q = q.filter(LeaveRequest.status == status)
    if from_date is not None:
        q = q.filter(LeaveRequest.start_date >= from_date)
    if to_date is not None:
        q = q.filter(LeaveRequest.end_date <= to_date)

    return q.all()


# ✅ Lấy 1 đơn theo id
@router.get("/{leave_id}", response_model=LeaveOut)
def get_leave(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return leave


# ✅ Update đơn (chỉ cho sửa khi đang pending)
@router.put("/{leave_id}", response_model=LeaveOut)
def update_leave(
    leave_id: int, data: LeaveUpdate, db: Session = Depends(get_db)
):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    if leave.status != "pending":
        raise HTTPException(
            status_code=400, detail="Only pending requests can be updated"
        )

    for key, value in data.dict(exclude_unset=True).items():
        setattr(leave, key, value)

    db.commit()
    db.refresh(leave)
    return leave


# ✅ Duyệt đơn
@router.put("/{leave_id}/approve", response_model=LeaveOut)
def approve_leave(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    leave.status = "approved"
    db.commit()
    db.refresh(leave)
    return leave


# ✅ Từ chối đơn
@router.put("/{leave_id}/reject", response_model=LeaveOut)
def reject_leave(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    leave.status = "rejected"
    db.commit()
    db.refresh(leave)
    return leave


# ✅ Xoá đơn
@router.delete("/{leave_id}")
def delete_leave(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    db.delete(leave)
    db.commit()
    return {"message": "Leave request deleted successfully"}
