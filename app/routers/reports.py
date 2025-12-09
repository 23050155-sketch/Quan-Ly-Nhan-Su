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


from app.core.security import get_current_admin, get_current_user
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
    
    

# =========================
# SALARY SLIP PDF CHO 1 NHÂN VIÊN / 1 THÁNG
# =========================
@router.get("/payroll-slip-pdf")
def export_payroll_slip_pdf(
    employee_id: int,
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Xuất phiếu lương PDF cho 1 nhân viên trong 1 tháng cụ thể.
    - Admin: xem được phiếu lương của bất kỳ ai
    - Nhân viên: chỉ xem được phiếu lương của chính mình
    """

    # 🔐 Check quyền
    if current_user.role != "admin":
        # Nếu không phải admin thì bắt buộc employee_id phải trùng với employee_id của user
        if current_user.employee_id is None or current_user.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không được phép xem phiếu lương của nhân viên khác",
            )

    # Lấy payroll + employee
    result = (
        db.query(Payroll, Employee)
        .join(Employee, Payroll.employee_id == Employee.id)
        .filter(
            Payroll.employee_id == employee_id,
            Payroll.year == year,
            Payroll.month == month,
        )
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bảng lương của nhân viên trong tháng này",
        )

    payroll, emp = result

    # Tạo file PDF
    filename = f"salary_slip_{employee_id}_{year}_{month}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)

    # Khởi tạo layout đơn giản
    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, y, "PHIẾU LƯƠNG NHÂN VIÊN")
    y -= 30

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Tháng/Năm: {month}/{year}")
    y -= 20
    c.drawString(50, y, f"Họ tên: {emp.full_name}")
    y -= 20
    if emp.position:
        c.drawString(50, y, f"Chức vụ: {emp.position}")
        y -= 20
    if emp.department:
        c.drawString(50, y, f"Phòng ban: {emp.department}")
        y -= 20

    y -= 10
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Chi tiết lương:")
    y -= 20
    c.setFont("Helvetica", 11)

    # Format số tiền cho đẹp
    def fmt_money(v: float) -> str:
        try:
            return f"{v:,.0f} VND"
        except Exception:
            return f"{v} VND"

    lines = [
        f"Số ngày làm việc       : {payroll.attendance_days}",
        f"Số ngày nghỉ có phép   : {payroll.paid_leave_days}",
        f"Lương cơ bản 1 ngày    : {fmt_money(payroll.base_daily_salary)}",
        f"Tổng lương (gross)     : {fmt_money(payroll.gross_salary)}",
        f"Khấu trừ               : {fmt_money(payroll.deductions)}",
        f"Lương thực nhận (net)  : {fmt_money(payroll.net_salary)}",
    ]

    for line in lines:
        c.drawString(70, y, line)
        y -= 18

    y -= 20
    c.drawString(50, y, "Ghi chú: Phiếu lương này được tạo tự động từ hệ thống HR.")
    y -= 40

    c.drawRightString(width - 50, y, "Người lập phiếu")
    y -= 60

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, 30, "Hệ thống HR Employee Management")

    c.save()

    return FileResponse(
        filename,
        media_type="application/pdf",
        filename=filename,
    )


