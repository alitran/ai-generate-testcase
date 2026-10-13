"""Build model input and validate generated testcase JSON."""
from __future__ import annotations
import json
import re
from typing import Any

REQUIRED_CASE_FIELDS = (
    "test_case_id", "requirement_ref", "title", "priority", "test_type",
    "preconditions", "test_data", "steps", "expected_result",
    "needs_clarification", "clarification_question",
)


def build_generation_input(task_template: str, requirement_text: str) -> str:
    if "{text}" not in task_template:
        raise ValueError("Task prompt phải chứa placeholder {text}")
    if not requirement_text.strip():
        raise ValueError("Requirement đang trống")
    return task_template.replace("{text}", requirement_text.strip())


def parse_json_report(output_text: str) -> dict[str, Any]:
    text = (output_text or "").strip().lstrip("\ufeff").strip()
    if not text:
        raise ValueError(
            "Model trả về nội dung rỗng. Hãy kiểm tra model Ollama, context/token limit "
            "và nội dung response của provider."
        )

    # Remove a surrounding Markdown code fence when the model adds one.
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

    try:
        report = json.loads(text)
    except json.JSONDecodeError as original_error:
        # Some local models prepend a short sentence or reasoning text. Try to
        # decode the first JSON object, then still apply strict schema validation.
        start = text.find("{")
        if start >= 0:
            try:
                report, _ = json.JSONDecoder().raw_decode(text[start:])
            except json.JSONDecodeError:
                preview = repr(text[:300])
                raise ValueError(
                    "Model không trả về JSON hợp lệ. Phản hồi bắt đầu bằng: "
                    f"{preview}. Hãy bật JSON mode hoặc kiểm tra model/prompt."
                ) from original_error
        else:
            preview = repr(text[:300])
            raise ValueError(
                "Model không trả về JSON object. Phản hồi bắt đầu bằng: "
                f"{preview}. Hãy bật JSON mode hoặc kiểm tra model/prompt."
            ) from original_error

    validate_report(report)
    return report


def validate_report(report: Any) -> None:
    if not isinstance(report, dict):
        raise ValueError("Kết quả phải là một JSON object")
    if not isinstance(report.get("test_cases"), list):
        raise ValueError("Thiếu mảng test_cases")
    if not isinstance(report.get("requirement_gaps", []), list):
        raise ValueError("requirement_gaps phải là mảng")
    if not isinstance(report.get("assumptions", []), list):
        raise ValueError("assumptions phải là mảng")

    seen_ids = set()
    for idx, case in enumerate(report["test_cases"], start=1):
        if not isinstance(case, dict):
            raise ValueError(f"Testcase #{idx} phải là object")
        missing = [key for key in REQUIRED_CASE_FIELDS if key not in case]
        if missing:
            raise ValueError(f"Testcase #{idx} thiếu field: {', '.join(missing)}")
        for key in ("test_case_id", "requirement_ref", "title", "priority", "test_type", "expected_result"):
            if not isinstance(case[key], str) or not case[key].strip():
                raise ValueError(f"Testcase #{idx}: {key} không được để trống")
        if case["test_case_id"] in seen_ids:
            raise ValueError(f"ID testcase bị trùng: {case['test_case_id']}")
        seen_ids.add(case["test_case_id"])
        if not isinstance(case["steps"], list) or not case["steps"]:
            raise ValueError(f"Testcase #{idx}: steps phải là mảng không rỗng")
        if not all(isinstance(step, str) and step.strip() for step in case["steps"]):
            raise ValueError(f"Testcase #{idx}: mỗi step phải là chuỗi không rỗng")
        if not isinstance(case["needs_clarification"], bool):
            raise ValueError(f"Testcase #{idx}: needs_clarification phải là boolean")
        if not isinstance(case["clarification_question"], str):
            raise ValueError(f"Testcase #{idx}: clarification_question phải là chuỗi")
