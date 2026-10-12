# Feature: Login

## User story
Là người dùng đã đăng ký, tôi muốn đăng nhập bằng email và password để truy cập dashboard.

## Acceptance Criteria
- AC-01: Login form có trường Email và Password.
- AC-02: Email và Password là trường bắt buộc.
- AC-03: Khi nhập email đã đăng ký và password đúng, hệ thống đăng nhập thành công và chuyển đến Dashboard.
- AC-04: Khi email hoặc password không đúng, hệ thống hiển thị thông báo chung: "Email hoặc mật khẩu không đúng".
- AC-05: Sau 5 lần đăng nhập thất bại liên tiếp, tài khoản bị khóa đăng nhập trong 15 phút.
- AC-06: Password được che mặc định. Người dùng có thể bật/tắt hiển thị password.

## Out of scope
- Quên mật khẩu.
- Đăng ký tài khoản.
- Đăng nhập bằng Google/Apple.

## Notes
- Không có yêu cầu cụ thể về email không đúng định dạng, thời gian session, CAPTCHA hoặc chính sách unlock thủ công. Hãy ghi chúng vào requirement_gaps nếu cần, không tự suy đoán expected result.
