"""Write generated testcases into reviewable JSON, CSV and Markdown."""
from __future__ import annotations
import csv
import json
from pathlib import Path
from typing import Any

CSV_FIELDS = [
    "test_case_id", "requirement_ref", "title", "priority", "test_type",
    "preconditions", "test_data", "steps", "expected_result",
    "needs_clarification", "clarification_question",
]


def write_report(report: dict[str, Any], output_dir: Path, stem: str) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{stem}_testcases.json"
    csv_path = output_dir / f"{stem}_testcases.csv"
    notes_path = output_dir / f"{stem}_review_notes.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for case in report["test_cases"]:
            row = dict(case)
            row["steps"] = "\n".join(f"{i}. {step}" for i, step in enumerate(case["steps"], start=1))
            row["needs_clarification"] = "Yes" if case["needs_clarification"] else "No"
            writer.writerow(row)

    lines = ["# Testcase review notes", "", f"Số testcase: {len(report['test_cases'])}", ""]
    gaps = report.get("requirement_gaps", [])
    assumptions = report.get("assumptions", [])
    flagged = [c for c in report["test_cases"] if c["needs_clarification"]]
    lines += ["## Requirement gaps / câu hỏi cần xác nhận", ""]
    lines += [f"- {item}" for item in gaps] or ["- Không có câu hỏi nào được ghi nhận."]
    lines += ["", "## Testcase cần làm rõ", ""]
    lines += [f"- **{c['test_case_id']} — {c['title']}**: {c['clarification_question'] or 'Cần review expected result.'}" for c in flagged] or ["- Không có testcase được đánh dấu cần làm rõ."]
    lines += ["", "## Assumptions — cần QA xác nhận", ""]
    lines += [f"- {item}" for item in assumptions] or ["- Không có giả định được ghi nhận."]
    lines += ["", "> Đây là bản nháp do AI tạo. Cần QA review trước khi nhập vào test management hoặc dùng làm release evidence.", ""]
    notes_path.write_text("\n".join(lines), encoding="utf-8")
    return {"json": json_path, "csv": csv_path, "notes": notes_path}
