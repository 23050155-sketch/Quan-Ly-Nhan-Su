from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.core.security import get_password_hash, get_current_admin

router = APIRouter(prefix="/users", tags=["Users"])


# ====== LẤY DANH SÁCH USER (ADMIN) ======
@router.get("/", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return db.query(User).all()


# ====== LẤY 1 USER THEO ID (ADMIN) ======
@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    return user


# ====== TẠO USER MỚI (ADMIN) ======
@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    # check trùng username
    existed = db.query(User).filter(User.username == user_in.username).first()
    if existed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username đã tồn tại",
        )

    # hash mật khẩu
    hashed_pw = get_password_hash(user_in.password)

    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hashed_pw,               # ✅ dùng password_hash
        role=user_in.role or "employee",
        employee_id=user_in.employee_id,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ====== XÓA USER (ADMIN) ======
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")

    db.delete(user)
    db.commit()
    return {"detail": "Xóa user thành công"}
