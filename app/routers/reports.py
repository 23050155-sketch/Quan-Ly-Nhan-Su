from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.payroll import Payroll
from app.models.attendance import Attendance
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

router = APIRouter(prefix="/reports", tags=["Reports"])

# =========================
# EXPORT BANG LUONG EXCEL
# =========================
@router.get("/payroll-excel")
def export_payroll_excel(db: Session = Depends(get_db)):
    payrolls = db.query(Payroll).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Bang luong"

    ws.append([
        "ID", "Nhan vien", "Thang", "Nam",
        "So ngay lam", "Luong 1 ngay",
        "Tong luong", "Khau tru", "Luong thuc"
    ])

    for p in payrolls:
        ws.append([
            p.id, p.employee_id, p.month, p.year,
            p.attendance_days, p.base_daily_salary,
            p.gross_salary, p.deductions, p.net_salary
        ])

    filename = "bang_luong.xlsx"
    wb.save(filename)

    return FileResponse(
        filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename
    )

# =========================
# EXPORT BANG LUONG PDF
# =========================
@router.get("/payroll-pdf")
def export_payroll_pdf(db: Session = Depends(get_db)):
    payrolls = db.query(Payroll).all()

    filename = "bang_luong.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    y = 800
    c.setFont("Helvetica", 10)

    c.drawString(200, y, "BANG LUONG NHAN VIEN")
    y -= 30

    for p in payrolls:
        line = f"NV {p.employee_id} | {p.month}/{p.year} | Luong thuc: {p.net_salary}"
        c.drawString(50, y, line)
        y -= 20

        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = 800

    c.save()
    return FileResponse(filename, media_type="application/pdf", filename=filename)

# =========================
# EXPORT CHAM CONG EXCEL
# =========================
@router.get("/attendance-excel")
def export_attendance_excel(db: Session = Depends(get_db)):
    # Lấy toàn bộ bản ghi chấm công
    attends = db.query(Attendance).all()

    # Tạo file Excel mới
    wb = Workbook()
    ws = wb.active
    ws.title = "Cham cong"

    # Header
    ws.append(["ID", "Nhan vien", "Ngay", "Gio vao", "Gio ra", "Trang thai"])

    # Ghi từng dòng dữ liệu
    for a in attends:
        # Tự tính trạng thái: có check_in thì "Có mặt", không có thì "Vắng"
        status = "Có mặt" if a.check_in is not None else "Vắng"

        ws.append([
            a.id,
            a.employee_id,
            str(a.date),
            str(a.check_in) if a.check_in else "",
            str(a.check_out) if a.check_out else "",
            status
        ])

    # Lưu file
    filename = "cham_cong.xlsx"
    wb.save(filename)

    # Trả file về cho client tải
    return FileResponse(
        filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename
    )

