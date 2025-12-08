from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.security import get_current_admin, get_current_user
from app.models.user import User

from app.database import get_db
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeOut

router = APIRouter(prefix="/employees", tags=["Employees"])


# ============ CREATE (admin-only) ============
@router.post("/", response_model=EmployeeOut, status_code=201)
def create_employee(
    emp: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),  # 👈 chỉ admin được tạo
):
    new_emp = Employee(**emp.dict())
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp


# ============ READ ALL (admin-only) ============
@router.get("/", response_model=List[EmployeeOut])
def get_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),  # 👈 chỉ admin xem list
):
    return db.query(Employee).all()


# ============ READ ONE (admin hoặc chính mình) ============
@router.get("/{emp_id}", response_model=EmployeeOut)
def get_employee(
    emp_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 👈 chỉ cần đăng nhập
):
    # nếu không phải admin, bắt buộc emp_id phải trùng employee_id của user
    if current_user.role != "admin" and current_user.employee_id != emp_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không được phép xem hồ sơ của người khác",
        )

    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên")
    return emp


# ============ UPDATE (admin-only) ============
@router.put("/{emp_id}", response_model=EmployeeOut)
def update_employee(
    emp_id: int,
    emp_update: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),  # 👈 chỉ admin sửa
):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên")

    for key, value in emp_update.dict(exclude_unset=True).items():
        setattr(emp, key, value)

    db.commit()
    db.refresh(emp)
    return emp


# ============ DELETE (admin-only) ============
@router.delete("/{emp_id}")
def delete_employee(
    emp_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),  # 👈 chỉ admin xóa
):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên")

    db.delete(emp)
    db.commit()
    return {"message": "Xóa nhân viên thành công"}
