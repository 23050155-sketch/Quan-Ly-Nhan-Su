from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

from app.database import Base, engine
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave_request import LeaveRequest
from app.models.payroll import Payroll
from app.models.user import User

# Routers
from app.routers.stats import router as stats_router
from app.routers import reports
from app.routers import auth
from app.routers import dashboard
from app.routers import users

from app.routers.employee import router as employee_router
from app.routers.attendance import router as attendance_router
from app.routers.leave_request import router as leave_router
from app.routers.payroll import router as payroll_router

# Tạo bảng MySQL nếu chưa có
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HR Employee Management API")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# STATIC FILES
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Debug
print(">>> USING STATIC FOLDER:", FRONTEND_DIR)

app.mount(
    "/frontend",
    StaticFiles(directory=str(FRONTEND_DIR), html=True),
    name="frontend",
)

# --- ROUTERS ---
app.include_router(auth.router)
app.include_router(employee_router)
app.include_router(attendance_router)
app.include_router(leave_router)
app.include_router(payroll_router)
app.include_router(stats_router)
app.include_router(reports.router)
app.include_router(dashboard.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"status": "OK", "message": "HR API is running!"}