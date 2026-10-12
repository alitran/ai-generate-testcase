"""Read text requirements only from this project's data/raw directory."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW_DIR = (PROJECT_ROOT / "data" / "raw").resolve()


def read_requirement(path: str) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    resolved = candidate.resolve()
    if resolved == DATA_RAW_DIR or DATA_RAW_DIR not in resolved.parents:
        raise ValueError("Chỉ được đọc file nằm bên trong data/raw/")
    if resolved.suffix.lower() not in {".txt", ".md"}:
        raise ValueError("Chỉ hỗ trợ file requirement .txt hoặc .md")
    if not resolved.is_file():
        raise FileNotFoundError(f"Không tìm thấy requirement: {resolved}")
    text = resolved.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("Requirement đang trống")
    return text
