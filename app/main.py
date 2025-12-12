# app/main.py
# app/main.py
from app.core.security import get_password_hash

from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv
from passlib.context import CryptContext

from app.database import Base, engine, SessionLocal
from app.models import (
    employee,
    attendance,
    leave_request,
    payroll,
    user,
    performance_review,
    compliance,
)

from app.models.user import User

from app.routers import auth, reports, dashboard
from app.routers.employee import router as employee_router
from app.routers.attendance import router as attendance_router
from app.routers.leave_request import router as leave_router
from app.routers.payroll import router as payroll_router
from app.routers.stats import router as stats_router
from app.routers.users import router as users_router
from app.routers.performance_review import router as performance_review_router
from app.routers.compliance import router as compliance_router


# ====== LOAD ENV ======
load_dotenv()

# ====== PASSWORD HASH ======
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# ====== SEED DEFAULT USER ======
def seed_default_admin():
    db = SessionLocal()
    try:
        username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
        email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@company.local")


        existed = db.query(User).filter(User.username == username).first()
        if existed:
            return

        admin = User(
            username=username,
            role="admin",
            email=email,
            employee_id=None,
            password_hash = get_password_hash(password)
        )


        db.add(admin)
        db.commit()
        print(f"✅ Seeded default admin: {username}")

    except Exception as e:
        db.rollback()
        print("❌ Seed admin failed:", e)
    finally:
        db.close()


# ====== TẠO APP ======
app = FastAPI(title="HR Employee Management", version="1.0.0")

# Tạo bảng
Base.metadata.create_all(bind=engine)


# ====== RUN SEED KHI START APP ======
@app.on_event("startup")
def on_startup():
    seed_default_admin()


# ====== CORS ======
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ====== STATIC FILES ======
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "front-end"

app.mount(
    "/assets",
    StaticFiles(directory=FRONTEND_DIR / "assets"),
    name="assets",
)

app.mount(
    "/html",
    StaticFiles(directory=FRONTEND_DIR / "html"),
    name="html",
)


# ====== ROUTERS ======
app.include_router(auth.router)
app.include_router(employee_router)
app.include_router(attendance_router)
app.include_router(leave_router)
app.include_router(payroll_router)
app.include_router(stats_router)
app.include_router(reports.router)
app.include_router(dashboard.router)
app.include_router(users_router)
app.include_router(performance_review_router)
app.include_router(compliance_router)


# ====== HEALTH CHECK ======
@app.get("/")
def root():
    return {"status": "OK", "message": "HR API is running"}
