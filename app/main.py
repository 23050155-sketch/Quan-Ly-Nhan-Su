from fastapi import FastAPI
from app.database import Base, engine
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave_request import LeaveRequest
from app.models.payroll import Payroll
from app.routers.stats import router as stats_router
from app.routers import reports
 
from app.routers.employee import router as employee_router
from app.routers.attendance import router as attendance_router
from app.routers.leave_request import router as leave_router
from app.routers.payroll import router as payroll_router

# Tạo bảng trong MySQL nếu chưa có
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HR Employee Management")

# 🔥 QUAN TRỌNG: gắn router Employees vào app
app.include_router(employee_router)
app.include_router(attendance_router)
app.include_router(leave_router)
app.include_router(payroll_router)
app.include_router(stats_router)
app.include_router(reports.router)

@app.get("/")
def root():
    return {"status": "OK", "message": "HR API is running"}