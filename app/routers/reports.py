from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.database import get_db
from app.models.payroll import Payroll
from app.models.attendance import Attendance
from app.models.employee import Employee


from app.core.security import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["Reports"])


# =========================
# EXPORT BẢNG LƯƠNG EXCEL (ADMIN)
# =========================
@router.get("/payroll-excel")
def export_payroll_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    payrolls = (
        db.query(Payroll, Employee)
        .join(Employee, Payroll.employee_id == Employee.id)
        .all()
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Bang luong"

    ws.append([
        "ID", "Ten nhan vien", "Thang", "Nam",
        "So ngay lam", "Luong 1 ngay",
        "Tong luong", "Khau tru", "Luong thuc"
    ])

    for p, e in payrolls:
        ws.append([
            p.id,
            e.full_name,             
            p.month,
            p.year,
            p.attendance_days,
            p.base_daily_salary,
            p.gross_salary,
            p.deductions,
            p.net_salary
        ])

    filename = "bang_luong.xlsx"
    wb.save(filename)

    return FileResponse(
        filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename
    )



# =========================
# EXPORT BẢNG LƯƠNG PDF (ADMIN)
# =========================
@router.get("/payroll-pdf")
def export_payroll_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    payrolls = (
        db.query(Payroll, Employee)
        .join(Employee, Payroll.employee_id == Employee.id)
        .all()
    )

    filename = "bang_luong.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    y = 800
    c.setFont("Helvetica", 10)

    c.drawString(200, y, "BANG LUONG NHAN VIEN")
    y -= 30

    for p, e in payrolls:
        line = f"{e.full_name} | {p.month}/{p.year} | Luong thuc: {p.net_salary}"
        c.drawString(50, y, line)
        y -= 20

        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = 800

    c.save()
    return FileResponse(filename, media_type="application/pdf", filename=filename)



# =========================
# EXPORT CHẤM CÔNG EXCEL (ADMIN)
# =========================
@router.get("/attendance-excel")
def export_attendance_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    attends = (
        db.query(Attendance, Employee)
        .join(Employee, Attendance.employee_id == Employee.id)
        .all()
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Cham cong"

    ws.append([
        "ID",
        "Ten nhan vien",     # ✅ TÊN
        "Ngay",
        "Gio vao",
        "Gio ra",
        "Trang thai"
    ])

    for a, e in attends:
        status_text = "Có mặt" if a.check_in else "Vắng"

        ws.append([
            a.id,
            e.full_name,           
            str(a.date),
            str(a.check_in) if a.check_in else "",
            str(a.check_out) if a.check_out else "",
            status_text
        ])

    filename = "cham_cong.xlsx"
    wb.save(filename)

    return FileResponse(
        filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename
    )

