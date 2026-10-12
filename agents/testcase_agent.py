"""CLI entry point for requirement-to-testcase generation using pluggable AI providers."""
from __future__ import annotations
import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

from agents.tools.file_reader import PROJECT_ROOT, read_requirement
from agents.skills.testcase_generator import build_generation_input, parse_json_report
from agents.tools.report_writer import write_report
from agents.providers import build_provider, resolve_model, SUPPORTED_PROVIDERS

PROMPTS_DIR = PROJECT_ROOT / "prompts"
DEFAULT_INPUT = "data/raw/login_requirements.md"
DEFAULT_OUTPUT_DIR = "data/processed"
TRACE_PATH = PROJECT_ROOT / "evals" / "traces" / "traces.jsonl"


def load_prompt(relative_path: str) -> str:
    path = (PROMPTS_DIR / relative_path).resolve()
    if PROMPTS_DIR.resolve() not in path.parents:
        raise ValueError("Prompt path phải nằm trong prompts/")
    if not path.is_file():
        raise FileNotFoundError(f"Không tìm thấy prompt: {path}")
    return path.read_text(encoding="utf-8").strip()


def append_trace(record: dict[str, Any], trace_path: Path = TRACE_PATH) -> None:
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with trace_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def generate_testcases(
    input_path: str = DEFAULT_INPUT,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    *, provider: str | None = None, model: str | None = None,
    text_provider: Any | None = None, trace_path: Path | None = None,
) -> dict[str, Path]:
    load_dotenv(PROJECT_ROOT / ".env")
    selected_provider = (provider or os.getenv("AI_PROVIDER", "openai")).lower().strip()
    selected_model = resolve_model(selected_provider, model)
    requirement = read_requirement(input_path)
    system_prompt = load_prompt("system/testcase_writer.txt")
    task_prompt = load_prompt("tasks/generate_testcases.txt")
    model_input = build_generation_input(task_prompt, requirement)
    llm = text_provider or build_provider(selected_provider)

    started = time.perf_counter()
    output_text = llm.generate(
        system_prompt=system_prompt,
        user_input=model_input,
        model=selected_model,
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    report = parse_json_report(output_text)
    out_dir = Path(output_dir)
    if not out_dir.is_absolute():
        out_dir = PROJECT_ROOT / out_dir
    stem = Path(input_path).stem
    paths = write_report(report, out_dir, stem)
    append_trace({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "success",
        "provider": selected_provider,
        "model": selected_model,
        "input_file": Path(input_path).name,
        "testcase_count": len(report["test_cases"]),
        "requirement_gap_count": len(report.get("requirement_gaps", [])),
        "clarification_count": sum(bool(c["needs_clarification"]) for c in report["test_cases"]),
        "latency_ms": elapsed_ms,
    }, trace_path or TRACE_PATH)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Sinh testcase từ requirement bằng một AI provider được chọn")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="File .md/.txt nằm trong data/raw/")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Thư mục ghi kết quả")
    parser.add_argument("--provider", choices=SUPPORTED_PROVIDERS, help="Ghi đè AI_PROVIDER trong .env")
    parser.add_argument("--model", help="Ghi đè model đã cấu hình cho provider")
    args = parser.parse_args()
    try:
        result_paths = generate_testcases(
            args.input, args.output_dir, provider=args.provider, model=args.model
        )
    except Exception as exc:
        parser.exit(status=1, message=f"Không tạo được testcase: {exc}\n")
    print("Đã tạo bản nháp testcase:")
    for kind, path in result_paths.items():
        print(f"- {kind}: {path}")
    print("Lưu ý: hãy review testcase, expected result và requirement gaps trước khi sử dụng.")


if __name__ == "__main__":
    main()
