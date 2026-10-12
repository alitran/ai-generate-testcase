"""Unit tests; the fake client avoids network calls and API cost."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from agents.skills.testcase_generator import build_generation_input, parse_json_report
from agents.testcase_agent import generate_testcases
from agents.tools.file_reader import PROJECT_ROOT

SAMPLE_REPORT = {
    "test_cases": [{
        "test_case_id": "TC-LOGIN-001",
        "requirement_ref": "AC-03",
        "title": "Đăng nhập với thông tin hợp lệ",
        "priority": "P1",
        "test_type": "Functional",
        "preconditions": "Tài khoản đã đăng ký và đang hoạt động",
        "test_data": "email=test@example.com; password=<valid-test-password>",
        "steps": ["Mở trang login", "Nhập email và password hợp lệ", "Nhấn Login"],
        "expected_result": "Đăng nhập thành công và chuyển đến Dashboard",
        "needs_clarification": False,
        "clarification_question": "",
    }],
    "requirement_gaps": [],
    "assumptions": [],
}


class FakeTextProvider:
    name = "fake"

    def __init__(self, output_text):
        self.output_text = output_text

    def generate(self, *, system_prompt, user_input, model):
        self.last_call = {
            "system_prompt": system_prompt,
            "user_input": user_input,
            "model": model,
        }
        return self.output_text


class TestcaseAgentTests(unittest.TestCase):
    def test_build_generation_input(self):
        self.assertIn("AC-01", build_generation_input("Requirement:\n{text}", "AC-01"))

    def test_parse_valid_json(self):
        parsed = parse_json_report(json.dumps(SAMPLE_REPORT, ensure_ascii=False))
        self.assertEqual(len(parsed["test_cases"]), 1)

    def test_reject_duplicate_ids(self):
        bad = dict(SAMPLE_REPORT)
        bad["test_cases"] = SAMPLE_REPORT["test_cases"] * 2
        with self.assertRaisesRegex(ValueError, "trùng"):
            parse_json_report(json.dumps(bad, ensure_ascii=False))

    def test_generate_files_without_real_api(self):
        raw_dir = PROJECT_ROOT / "data" / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        temp_input = raw_dir / "_unit_test_requirement.txt"
        try:
            temp_input.write_text("AC-03: valid login routes to Dashboard", encoding="utf-8")
            with tempfile.TemporaryDirectory() as tmp:
                trace = Path(tmp) / "trace.jsonl"
                paths = generate_testcases(
                    "data/raw/_unit_test_requirement.txt",
                    str(Path(tmp) / "out"),
                    provider="openai",
                    text_provider=FakeTextProvider(json.dumps(SAMPLE_REPORT, ensure_ascii=False)),
                    model="fake-model",
                    trace_path=trace,
                )
                self.assertTrue(paths["csv"].is_file())
                self.assertTrue(paths["json"].is_file())
                self.assertTrue(paths["notes"].is_file())
                self.assertIn("TC-LOGIN-001", paths["csv"].read_text(encoding="utf-8-sig"))
                self.assertTrue(trace.is_file())
                self.assertIn('"provider": "openai"', trace.read_text(encoding="utf-8"))
        finally:
            temp_input.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
