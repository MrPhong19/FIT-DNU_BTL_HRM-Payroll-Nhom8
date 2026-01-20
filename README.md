# BTL Odoo 15: Tích hợp Chấm công + Tính lương

**Nhóm:** Nhóm 8 - Lớp CNTT 17-09 
**Thành viên:**  
- Nguyễn Kiều Phong - 1771020538
- Nguyễn Xuân Phúc
- Nguyễn Thị Hảo Ngân

**Đề tài:** Tự động hóa tính lương dựa trên dữ liệu chấm công thực tế, kết nối hồ sơ nhân sự và bảo hiểm.

**Nguồn tham khảo & kế thừa:**  
- Kho Khoa FIT-DNU (base chính): https://github.com/FIT-DNU/Business-Internship  
- Repo khóa trước (tham khảo HRM/Attendance/Payroll): https://github.com/dinhtuananh188/TTDN-15-01-N5  

**Mô tả ngắn gọn:**  
- Kế thừa module Quản lý nhân sự (HRM) từ base Khoa và repo cũ.  
- Cải tiến chính: Tự động tính lương từ dữ liệu chấm công (giờ công hợp lệ, thưởng phạt muộn/về sớm, bảo hiểm tự động tính theo lương cơ bản + phụ cấp).  
- Mục tiêu: Đạt mức 2 (tự động hóa quy trình), hướng tới mức 3 (tích hợp AI/API nếu thời gian cho phép).  

**Cấu trúc thư mục:**  
- `addons/`: Custom modules và kế thừa từ base (sẽ tạo module `hr_attendance_payroll_custom`).  
- `docs/business_flow/`: Luồng nghiệp vụ BPMN (sẽ nộp sớm dưới dạng PDF/PNG).  
- README này sẽ cập nhật tiến độ commit và thay đổi.  

**Lưu ý:**  
- Commit thường xuyên để minh bạch lịch sử phát triển (tránh commit 1 lần cuối kỳ).  
- Tất cả code cải tiến sẽ được ghi nguồn rõ ràng theo yêu cầu môn học
