from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employee import Employee
from app.services.email_service import send_leave_status_email
from app.models.leave_request import LeaveRequest
from app.schemas.leave_request import (
    LeaveCreate,
    LeaveUpdate,
    LeaveOut,
)

from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/leaves", tags=["Leave Requests"])


# ✅ Tạo đơn xin nghỉ (mặc định status = pending)
@router.post("/", response_model=LeaveOut)
def create_leave(
    data: LeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Nhân viên chỉ được tạo đơn cho chính mình
    if current_user.role != "admin" and current_user.employee_id != data.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không được phép tạo đơn nghỉ cho nhân viên khác",
        )

    emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên")

    leave = LeaveRequest(**data.dict())
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave

    # 🔓 Endpoint PUBLIC cho form HTML (không cần login)
@router.post("/public", response_model=LeaveOut)
def create_leave_public(
    data: LeaveCreate,
    db: Session = Depends(get_db),
):
    # Kiểm tra nhân viên tồn tại
    emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên")

    leave = LeaveRequest(**data.dict())
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave


# ✅ Lấy danh sách đơn nghỉ
@router.get("/", response_model=List[LeaveOut])
def list_leaves(
    employee_id: Optional[int] = None,
    leave_status: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(LeaveRequest)

    if current_user.role != "admin":
        if employee_id is not None and employee_id != current_user.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không được phép xem đơn nghỉ của nhân viên khác",
            )
        q = q.filter(LeaveRequest.employee_id == current_user.employee_id)
    else:
        if employee_id is not None:
            q = q.filter(LeaveRequest.employee_id == employee_id)

    if leave_status is not None:
        q = q.filter(LeaveRequest.status == leave_status)
    if from_date is not None:
        q = q.filter(LeaveRequest.start_date >= from_date)
    if to_date is not None:
        q = q.filter(LeaveRequest.end_date <= to_date)

    return q.all()



# Lấy 1 đơn theo id
@router.get("/{leave_id}", response_model=LeaveOut)
def get_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn xin nghỉ")

    # Nhân viên chỉ xem đơn của chính mình
    if current_user.role != "admin" and current_user.employee_id != leave.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không được phép xem đơn nghỉ của người khác",
        )

    return leave


# Update đơn (chỉ cho sửa khi đang pending)
@router.put("/{leave_id}", response_model=LeaveOut)
def update_leave(
    leave_id: int,
    data: LeaveUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn xin nghỉ")

    # Nhân viên chỉ sửa đơn của mình
    if current_user.role != "admin" and current_user.employee_id != leave.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không được phép sửa đơn nghỉ của người khác",
        )

    if leave.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Chỉ đơn đang chờ duyệt mới được chỉnh sửa",
        )

    for key, value in data.dict(exclude_unset=True).items():
        setattr(leave, key, value)

    db.commit()
    db.refresh(leave)
    return leave


# Duyệt đơn (chỉ admin)
@router.put("/{leave_id}/approve", response_model=LeaveOut)
def approve_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ quản trị viên mới được phép duyệt đơn",
        )

    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn xin nghỉ")

    leave.status = "approved"
    db.commit()
    db.refresh(leave)
    
    # GỬI EMAIL THÔNG BÁO ĐƯỢC DUYỆT
    try:
        emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
        if emp:
            send_leave_status_email(
                employee_email=emp.email,
                employee_name=emp.full_name,
                leave_id=leave.id,
                status=leave.status,
            )
    except Exception as e:
        print(f"[EMAIL] Lỗi khi gửi email duyệt đơn nghỉ: {e}")
    
    return leave


# Từ chối đơn (chỉ admin)
@router.put("/{leave_id}/reject", response_model=LeaveOut)
def reject_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ quản trị viên mới được phép từ chối đơn",
        )

    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn xin nghỉ")

    leave.status = "rejected"
    db.commit()
    db.refresh(leave)
    
    # GỬI EMAIL THÔNG BÁO BỊ TỪ CHỐI
    try:
        emp = db.query(Employee).filter(Employee.id == leave.employee_id).first()
        if emp:
            send_leave_status_email(
                employee_email=emp.email,
                employee_name=emp.full_name,
                leave_id=leave.id,
                status=leave.status,
            )
    except Exception as e:
        print(f"[EMAIL] Lỗi khi gửi email từ chối đơn nghỉ: {e}")

    return leave


# Xoá đơn (chỉ admin)
@router.delete("/{leave_id}")
def delete_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ quản trị viên mới được phép xoá đơn nghỉ",
        )

    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn xin nghỉ")

    db.delete(leave)
    db.commit()
    return {"message": "Xoá đơn xin nghỉ thành công"}
