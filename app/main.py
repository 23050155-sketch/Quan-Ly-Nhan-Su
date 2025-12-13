# app/main.py
from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

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
from app.core.security import get_password_hash

from app.routers import auth, reports, dashboard
from app.routers.employee import router as employee_router
from app.routers.attendance import router as attendance_router
from app.routers.leave_request import router as leave_router
from app.routers.payroll import router as payroll_router
from app.routers.stats import router as stats_router
from app.routers.users import router as users_router
from app.routers.performance_review import router as performance_review_router
from app.routers.compliance import router as compliance_router

load_dotenv()

app = FastAPI()

def seed_default_admin():
    db = SessionLocal()
    try:
        username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
        email = os.getenv("DEFAULT_ADMIN_EMAIL", "quanlynhansu1415@gmail.com")

        existed = db.query(User).filter(User.username == username).first()
        if existed:
            existed.email = email
            db.commit()
            return

        admin = User(
            username=username,
            role="admin",
            email=email,
            employee_id=None,
            password_hash=get_password_hash(password)
        )

        db.add(admin)
        db.commit()
        print(f"✅ Seeded default admin: {username}")

    except Exception as e:
        db.rollback()
        print("❌ Seed admin failed:", e)
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    if os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true":
        try:
            Base.metadata.create_all(bind=engine)
            print("✅ Tables ensured (create_all).")
        except Exception as e:
            print("[WARN] DB not ready, skip create_all:", e)
            return
    seed_default_admin()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "front-end"

app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
app.mount("/html", StaticFiles(directory=FRONTEND_DIR / "html"), name="html")

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

@app.get("/")
def root():
    return {"status": "OK", "message": "HR API is running"}
