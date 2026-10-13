"""Deterministic, no-API-key provider for demonstrating the full report pipeline.

This provider returns canned fixture data. It does NOT use an AI model and does
NOT generate testcases from the supplied requirement. Use only to smoke-test
file reading, report validation, CSV/JSON export, and trace writing.
"""
from __future__ import annotations
import json
from typing import Any


DEMO_REPORT: dict[str, Any] = {
    "test_cases": [
        {
            "test_case_id": "TC-DEMO-001",
            "requirement_ref": "AC-03",
            "title": "Đăng nhập với thông tin hợp lệ",
            "priority": "P1",
            "test_type": "Functional",
            "preconditions": "Tài khoản demo đã đăng ký và đang hoạt động",
            "test_data": "email=demo@example.com; password=<valid-test-password>",
            "steps": [
                "Mở trang đăng nhập",
                "Nhập email và password hợp lệ đã được chuẩn bị",
                "Nhấn nút Login",
            ],
            "expected_result": "Người dùng đăng nhập thành công và được chuyển đến Dashboard",
            "needs_clarification": False,
            "clarification_question": "",
        },
        {
            "test_case_id": "TC-DEMO-002",
            "requirement_ref": "AC-02",
            "title": "Đăng nhập khi bỏ trống Email",
            "priority": "P1",
            "test_type": "Negative",
            "preconditions": "Đang ở trang đăng nhập",
            "test_data": "email=empty; password=<valid-test-password>",
            "steps": [
                "Mở trang đăng nhập",
                "Để trống trường Email",
                "Nhập password hợp lệ đã được chuẩn bị",
                "Nhấn nút Login",
            ],
            "expected_result": "Hệ thống không cho đăng nhập; nội dung validation cụ thể cần đối chiếu Acceptance Criteria/UI specification",
            "needs_clarification": True,
            "clarification_question": "Requirement có quy định nội dung và vị trí thông báo khi Email bị bỏ trống không?",
        },
        {
            "test_case_id": "TC-DEMO-003",
            "requirement_ref": "AC-04",
            "title": "Đăng nhập với thông tin không chính xác",
            "priority": "P1",
            "test_type": "Negative",
            "preconditions": "Tài khoản demo tồn tại; tài khoản chưa bị khóa",
            "test_data": "email=demo@example.com; password=<incorrect-test-password>",
            "steps": [
                "Mở trang đăng nhập",
                "Nhập email hợp lệ và password không chính xác",
                "Nhấn nút Login",
            ],
            "expected_result": "Hiển thị thông báo 'Email hoặc mật khẩu không đúng' và không đăng nhập",
            "needs_clarification": False,
            "clarification_question": "",
        },
    ],
    "requirement_gaps": [
        "Bản demo dùng dữ liệu fixture. Hãy xác nhận nội dung validation khi Email bị bỏ trống trước khi dùng testcase thực tế."
    ],
    "assumptions": [
        "Các testcase này là dữ liệu mẫu cố định để kiểm tra pipeline; không phải kết quả do AI suy luận từ requirement đầu vào."
    ],
}


class DemoProvider:
    name = "demo"

    def generate(self, *, system_prompt: str, user_input: str, model: str) -> str:
        # Arguments are intentionally accepted to match the common provider interface.
        return json.dumps(DEMO_REPORT, ensure_ascii=False)
