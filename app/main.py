from fastapi import FastAPI
from app.database import Base, engine
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave_request import LeaveRequest
from app.models.payroll import Payroll
from app.routers.stats import router as stats_router
from app.routers import reports
from app.models.user import User
 
from app.routers.employee import router as employee_router
from app.routers.attendance import router as attendance_router
from app.routers.leave_request import router as leave_router
from app.routers.payroll import router as payroll_router
from app.routers.auth import router as auth_router

# Tạo bảng trong MySQL nếu chưa có
Base.metadata.create_all(bind=engine)

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

app = FastAPI(
    title="HR Employee Management",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True
    }
)


# 🔥 QUAN TRỌNG: gắn router Employees vào app
app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(attendance_router)
app.include_router(leave_router)
app.include_router(payroll_router)
app.include_router(stats_router)
app.include_router(reports.router)

@app.get("/")
def root():
    return {"status": "OK", "message": "HR API is running"}





from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="HR Employee Management",
        version="1.0",
        description="HR System",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [
                {"BearerAuth": []}
            ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

