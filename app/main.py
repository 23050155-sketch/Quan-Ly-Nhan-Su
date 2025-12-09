from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.database import Base, engine
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave_request import LeaveRequest
from app.models.payroll import Payroll
from app.models.user import User

from app.routers.stats import router as stats_router
from app.routers import reports
from app.routers import auth
from app.routers import dashboard

 
from app.routers.employee import router as employee_router
from app.routers.attendance import router as attendance_router
from app.routers.leave_request import router as leave_router
from app.routers.payroll import router as payroll_router
from app.routers.auth import router as auth_router

# Tạo bảng trong MySQL nếu chưa có
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HR Employee Management")



# ======================
# SERVE FRONTEND STATIC
# ======================
BASE_DIR = Path(__file__).resolve().parent        # trỏ tới thư mục app
FRONTEND_DIR = BASE_DIR / "front-end"             # app/front-end

# Serve /html/*
app.mount(
    "/html",
    StaticFiles(directory=str(FRONTEND_DIR / "html"), html=True),
    name="html",
)

# Serve /assets/*
app.mount(
    "/assets",
    StaticFiles(directory=str(FRONTEND_DIR / "assets")),
    name="assets",
)




# 🔥 QUAN TRỌNG: gắn router Employees vào app
app.include_router(auth.router)
app.include_router(employee_router)
app.include_router(attendance_router)
app.include_router(leave_router)
app.include_router(payroll_router)
app.include_router(stats_router)
app.include_router(reports.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"status": "OK", "message": "HR API is running"}

    #abcd