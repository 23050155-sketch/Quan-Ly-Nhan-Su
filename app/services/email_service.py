# app/services/email_service.py
import os
from typing import Optional

import requests

RESEND_API_URL = "https://api.resend.com/emails"

def _send_resend(to_email: str, subject: str, text: Optional[str] = None, html: Optional[str] = None):
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        print("[EMAIL] Thiếu RESEND_API_KEY, không gửi được email.")
        return False

    mail_from = os.getenv("MAIL_FROM", "onboarding@resend.dev")
    mail_from_name = os.getenv("MAIL_FROM_NAME", "HR System")

    payload = {
        "from": f"{mail_from_name} <{mail_from}>",
        "to": [to_email],
        "subject": subject,
    }

    # Resend ưu tiên html, không có thì dùng text
    if html:
        payload["html"] = html
    else:
        payload["text"] = text or ""

    try:
        resp = requests.post(
            RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=20,
        )

        if resp.status_code >= 400:
            print(f"[EMAIL] Gửi email thất bại (Resend {resp.status_code}): {resp.text}")
            return False

        print(f"[EMAIL] Gửi email tới {to_email} thành công (Resend).")
        return True

    except Exception as e:
        print(f"[EMAIL] Gửi email thất bại: {e}")
        return False


# Giữ API hàm cũ để khỏi phải sửa các chỗ gọi
def send_email(to_email: str, subject: str, body: str):
    """
    Gửi email dạng text (dùng Resend).
    Nếu lỗi thì chỉ log ra console, không làm API bị crash.
    """
    return _send_resend(to_email=to_email, subject=subject, text=body)


def send_payroll_email(
    employee_email: Optional[str],
    employee_name: str,
    year: int,
    month: int,
    net_salary: float,
):
    if not employee_email:
        print(f"[EMAIL] Nhân viên {employee_name} chưa có email, bỏ qua.")
        return False

    subject = f"[HR] Phiếu lương tháng {month}/{year}"
    body = (
        f"Xin chào {employee_name},\n\n"
        f"Phiếu lương của bạn trong tháng {month}/{year} đã được tạo.\n"
        f" - Lương thực nhận: {net_salary:,.0f} VND\n\n"
        "Vui lòng đăng nhập hệ thống để xem chi tiết.\n\n"
        "Trân trọng,\n"
        "Phòng Nhân Sự"
    )

    return send_email(employee_email, subject, body)


def send_leave_status_email(
    employee_email: Optional[str],
    employee_name: str,
    leave_id: int,
    status: str,
):
    if not employee_email:
        print(f"[EMAIL] Nhân viên {employee_name} chưa có email, bỏ qua.")
        return False

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

    return send_email(employee_email, subject, body)
