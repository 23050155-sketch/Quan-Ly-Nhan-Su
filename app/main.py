# app/main.py

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv

from app.database import Base, engine
from app.models import employee, attendance, leave_request, payroll, user, performance_review, compliance

from app.routers import auth, reports, dashboard, compliance
from app.routers.employee import router as employee_router
from app.routers.attendance import router as attendance_router
from app.routers.leave_request import router as leave_router
from app.routers.payroll import router as payroll_router
from app.routers.stats import router as stats_router
from app.routers.users import router as users_router
from app.routers.performance_review import router as performance_review_router



# ====== LOAD ENV (SMTP_USER, SMTP_PASSWORD, ...) ======
load_dotenv()


# ====== TẠO APP ======
app = FastAPI(title="HR Employee Management", version="1.0.0")

# Tạo bảng trong DB (do đã import models ở trên)
Base.metadata.create_all(bind=engine)


# ====== CORS (cho frontend chạy cùng origin) ======
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # cần chặt hơn thì sửa lại origin cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ====== STATIC FILES (HTML + CSS/JS) ======
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "front-end"

# /assets/... -> app/front-end/assets/...
app.mount(
    "/assets",
    StaticFiles(directory=FRONTEND_DIR / "assets"),
    name="assets",
)

# /html/... -> app/front-end/html/...
app.mount(
    "/html",
    StaticFiles(directory=FRONTEND_DIR / "html"),
    name="html",
)


# ====== ROUTERS API ======
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