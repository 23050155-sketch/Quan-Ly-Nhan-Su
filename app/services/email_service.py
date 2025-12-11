# app/services/email_service.py

import os
from dotenv import load_dotenv


load_dotenv()


import smtplib
from email.message import EmailMessage
from typing import Optional


# Nên set mấy cái này qua biến môi trường cho đỡ lộ info
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")  # email gửi đi
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # app password hoặc mật khẩu


def send_email(
    to_email: str,
    subject: str,
    body: str,
):
    """
    Gửi email đơn giản dạng text.
    Nếu lỗi thì chỉ log ra console, không làm API bị crash.
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        print("[EMAIL] Thiếu SMTP_USER hoặc SMTP_PASSWORD, không gửi được email.")
        return

    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"[EMAIL] Gửi email tới {to_email} thành công.")
    except Exception as e:
        print(f"[EMAIL] Gửi email thất bại: {e}")


def send_payroll_email(
    employee_email: Optional[str],
    employee_name: str,
    year: int,
    month: int,
    net_salary: float,
):
    if not employee_email:
        print(f"[EMAIL] Nhân viên {employee_name} chưa có email, bỏ qua.")
        return

    subject = f"[HR] Phiếu lương tháng {month}/{year}"
    body = (
        f"Xin chào {employee_name},\n\n"
        f"Phiếu lương của bạn trong tháng {month}/{year} đã được tạo.\n"
        f" - Lương thực nhận: {net_salary:,.0f} VND\n\n"
        "Vui lòng đăng nhập hệ thống để xem chi tiết.\n\n"
        "Trân trọng,\n"
        "Phòng Nhân Sự"
    )

    send_email(employee_email, subject, body)


def send_leave_status_email(
    employee_email: Optional[str],
    employee_name: str,
    leave_id: int,
    status: str,
):
    if not employee_email:
        print(f"[EMAIL] Nhân viên {employee_name} chưa có email, bỏ qua.")
        return

    if status == "approved":
        status_text = "được chấp thuận ✅"
    elif status == "rejected":
        status_text = "bị từ chối ❌"
    else:
        status_text = f"chuyển sang trạng thái: {status}"

    subject = f"[HR] Cập nhật trạng thái đơn nghỉ #{leave_id}"
    body = (
        f"Xin chào {employee_name},\n\n"
        f"Đơn xin nghỉ #{leave_id} của bạn đã {status_text}.\n"
        "Vui lòng đăng nhập hệ thống để xem chi tiết.\n\n"
        "Trân trọng,\n"
        "Phòng Nhân Sự"
    )

    send_email(employee_email, subject, body)
