# QA Testcase Agent — scorecard

Chấm bản nháp theo thang 0/1/2 (0 = không đạt, 1 = một phần, 2 = đạt):

1. **Traceability** — testcase liên kết requirement/AC rõ ràng.
2. **Expected result grounded** — expected result không thêm rule chưa được nêu.
3. **Coverage** — bao phủ luồng chính và lỗi/biên phù hợp với requirement.
4. **Clarity** — precondition, data, steps, expected result có thể thực thi.
5. **No duplication** — không lặp lại cùng một mục tiêu kiểm thử.
6. **Gap detection** — ghi nhận thông tin thiếu dưới dạng câu hỏi cụ thể.
7. **Privacy** — không đưa dữ liệu thật/secret vào test data hoặc trace.

Tổng điểm tối đa: 14. Gợi ý ngưỡng thử nghiệm nội bộ: tối thiểu 11/14 và không có lỗi nghiêm trọng ở mục 2 hoặc 7. Đây là ngưỡng khởi đầu tham khảo, cần hiệu chỉnh theo tiêu chuẩn team.
