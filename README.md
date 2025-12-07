# 🧑‍💼 HR Employee Management System

Hệ thống quản lý nhân sự được xây dựng bằng **FastAPI + MySQL**, hỗ trợ đầy đủ các nghiệp vụ:
- Quản lý nhân viên
- Chấm công
- Xin nghỉ phép
- Tính lương
- Thống kê – báo cáo

Phục vụ cho bài tiểu luận môn **Phát triển ứng dụng mã nguồn mở**.

---

## 🚀 Công Nghệ Sử Dụng
- Python 3.12
- FastAPI
- SQLAlchemy
- MySQL
- Uvicorn
- Swagger UI

---

## 📦 Cài Đặt Môi Trường

### 1. Clone project
```bash
git clone https://github.com/23050155-sketch/Quan-Ly-Nhan-Su.git
cd Quan-Ly-Nhan-Su
2. Tạo môi trường ảo
bash
Sao chép mã
python3 -m venv venv
source venv/bin/activate
3. Cài thư viện
bash
Sao chép mã
pip install -r requirements.txt
🛠️ Cấu Hình Database MySQL
Tạo database:

sql
Sao chép mã
CREATE DATABASE hr_db;
Cập nhật thông tin kết nối trong:

bash
Sao chép mã
app/database.py
▶️ Chạy Ứng Dụng
bash
Sao chép mã
uvicorn app.main:app --reload
Truy cập Swagger:

bash
Sao chép mã
http://localhost:8000/docs
📂 Chức Năng Chính
👤 Quản Lý Nhân Viên
Thêm, sửa, xóa, xem nhân viên

⏱️ Chấm Công
Ghi nhận ngày làm việc

Cập nhật trạng thái đi làm

📝 Xin Nghỉ Phép
Tạo đơn nghỉ phép

Duyệt / từ chối đơn

💰 Tính Lương
Tự động tính lương theo:

Số ngày công

Số ngày nghỉ

Lương/ngày

Xem chi tiết bảng lương

📊 Thống Kê – Báo Cáo
Tổng nhân viên

Tổng ngày công

Thống kê lương theo tháng

Thống kê nghỉ phép

🔌 API Chính
Module	Endpoint
Employees	/employees
Attendance	/attendances
Leave Requests	/leaves
Payroll	/payrolls

👨‍🎓 Thông Tin Sinh Viên
Tên: Bùi Anh Dũng

MSSV: 23050155

Trường: Đại học Bình Dương

Môn: Phát triển ứng dụng mã nguồn mở

