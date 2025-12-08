from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import TokenData

# ====== CẤU HÌNH JWT ======
SECRET_KEY = "change-me-to-a-long-random-string"  # nhớ giữ cố định, đừng đổi liên tục
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 ngày

# tokenUrl không cần dấu /
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Dùng pbkdf2_sha256 cho chắc
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


# ====== HÀM HASH / VERIFY MẬT KHẨU ======
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ====== TẠO ACCESS TOKEN ======
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    # sub nên ép về string cho chuẩn
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ====== LẤY USER TỪ TOKEN ======
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực người dùng",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        username = payload.get("username")
        role = payload.get("role")

        token_data = TokenData(
            sub=int(user_id),
            username=username,
            role=role,
        )
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.sub).first()
    if user is None:
        raise credentials_exception
    return user


# ====== CHỈ ADMIN ======
async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới được phép thực hiện chức năng này",
        )
    return current_user


# ====== NHÂN VIÊN (HOẶC ADMIN) ======
async def get_current_employee(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role not in ["employee", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập",
        )
    return current_user
