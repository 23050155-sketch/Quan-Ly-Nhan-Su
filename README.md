# HR / Employee Management System

Hệ thống Quản lý Nhân Sự (HR / Employee Management) được xây dựng bằng FastAPI + MySQL, hỗ trợ đầy đủ các nghiệp vụ quản lý nhân viên trong doanh nghiệp như: quản lý hồ sơ nhân viên, chấm công, xin nghỉ phép, tính lương, thống kê – báo cáo.



# Mục Tiêu Dự Án

- Xây dựng một hệ thống HR dạng Web có tính thực tế và mở rộng

- Áp dụng kiến thức:

    + Backend API

    + ORM & Database

    + Xác thực – phân quyền

- Hệ thống có thể sử dụng cho doanh nghiệp nhỏ và vừa



# Công Nghệ Sử Dụng
* Backend:
        Python 3.12,
        FastAPI,
        SQLAlchemy ORM,
        JWT Authentication,
        Uvicorn,
        Swagger UI

* Database:
        MySQL

* Frontend:
        HTML,
        CSS,
        JavaScript (Vanilla JS)

* Môi Trường Phát Triển:
        VSCode,
        SSH Remote,
        Oracle VirtualBox (Linux VM)



# Kiến Trúc Hệ Thống
Browser (HTML/CSS/JS)
        ↓
FastAPI Backend (REST API)
        ↓
  MySQL Database

- Frontend gọi API thông qua HTTP
- Backend xử lý nghiệp vụ và truy xuất dữ liệu
- Database lưu trữ toàn bộ thông tin nhân sự



# Cài Đặt & Chạy Dự Án
1. Clone Project:
- git clone https://github.com/23050155-sketch/Quan-Ly-Nhan-Su.git
- cd Quan-Ly-Nhan-Su

2. Tạo môi trường ảo:
- python3 -m venv venv
- source venv/bin/activate

3. Cài đặt thư viện:
- pip install -r requirements.txt

4. Cấu hình Database MySQL:
    - Tạo Database:
        CREATE DATABASE hr_db;
    - Cập nhật chuỗi kết nối trong file:
        app/database.py -> DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/hr_db"

5. Chạy ứng dụng:
- uvicorn app.main:app --reload

6. Truy cập:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/html/login.html (Đăng nhập) -> Tài khoản User quyền truy cập admin mặc định có trong main.py



# Xác Thực & Phân Quyền
Hệ thống sử dụng JWT (JSON Web Token):

- Admin
    Toàn quyền quản lý hệ thống,
    Quản lý nhân viên, lương, nghỉ phép, thống kê

- Employee
    Chỉ thao tác dữ liệu cá nhân,
    Không truy cập dữ liệu người khác



# Chức Năng Chính

1. Quản Lý Nhân Viên:
Thêm / sửa / xóa / xem nhân viên,
Lưu thông tin: họ tên, email, giới tính, chức vụ, lương/ngày

2. Chấm Công:
Ghi nhận ngày làm việc,
Theo dõi trạng thái: đi làm, nghỉ, đi muộn
Hiển thị lịch sử chấm công

3. Xin Nghỉ Phép:
Nhân viên gửi đơn xin nghỉ,
Admin duyệt / từ chối,
Cập nhật trạng thái đơn nghỉ

4. Tính Lương:
Tính lương tự động theo tháng dựa trên:
Số ngày công,
Số ngày nghỉ có phép,
Lương/ngày,
Nhân viên xem chi tiết bảng lương

5. Thống Kê – Báo Cáo:
Tổng số nhân viên,
Tổng ngày công,
Thống kê lương theo tháng,
Thống kê nghỉ phép,
Dashboard tổng quan hệ thống



# API Chính
![Api Main](app/docs/screenshots/api-main.png)



# Cấu Trúc Thư Mục
![Cấu Trúc Thư Mục](app/docs/screenshots/cau-truc-thu-muc.png)



# Demo Hệ Thống

1. Trang đăng nhập:
![Login](app/docs/screenshots/login.png)

2. Admin Dashboard:
![Admin Dashboard](app/docs/screenshots/admin-dashboard.png)

3. Employee Home:
![Employee Home](app/docs/screenshots/employee-home.png)

4. Swagger:
![Swagger](app/docs/screenshots/swagger.png)



# Thông Tin Sinh Viên

1. Sinh viên 1:
- Họ tên: Bùi Anh Dũng
- MSSV: 23050155
- Trường: Đại học Bình Dương
- Môn: Phát triển ứng dụng mã nguồn mở

2. Sinh viên 2:
- Họ tên: Nguyễn Quang Hoài Đức
- MSSV: 23050181
- Trường: Đại học Bình Dương
- Môn: Phát triển ứng dụng mã nguồn mở



# Kết luận
Dự án đã xây dựng thành công một hệ thống HR / Employee Management với đầy đủ chức năng cơ bản và nâng cao, đáp ứng tốt yêu cầu của môn học cũng như có khả năng mở rộng trong thực tế.
