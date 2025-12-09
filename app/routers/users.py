from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.core.security import get_password_hash, get_current_admin

router = APIRouter(prefix="/users", tags=["Users"])


# ========== GET ALL USERS ==========
@router.get("/", response_model=list[UserOut])
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    return db.query(User).all()


# ========== GET USER BY ID ==========
@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ========== CREATE USER ==========
@router.post("/", response_model=UserOut)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    existed = db.query(User).filter(User.username == user_in.username).first()
    if existed:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=user_in.username,
        email=user_in.email,
        password=get_password_hash(user_in.password),
        role=user_in.role,
        employee_id=user_in.employee_id,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ========== UPDATE USER ==========
@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_in: UserUpdate,   # ✅ dùng UserUpdate, không phải UserCreate
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.username = user_in.username
    user.email = user_in.email
    user.role = user_in.role
    user.employee_id = user_in.employee_id

    # chỉ đổi password nếu client gửi kèm
    if user_in.password:
        user.password = get_password_hash(user_in.password)

    db.commit()
    db.refresh(user)
    return user



# ========== DELETE USER ==========
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "Deleted successfully"}
