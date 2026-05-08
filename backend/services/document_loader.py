from __future__ import annotations

from pathlib import Path
from typing import Dict, List


def _read_text_file(file_path: Path) -> str:
    for encoding in ("utf-8", "cp949"):
        try:
            return file_path.read_text(encoding=encoding).strip()
        except UnicodeDecodeError:
            continue
    return ""


def load_txt_documents(directory: Path) -> List[Dict[str, str]]:
    documents: List[Dict[str, str]] = []
    if not directory.exists():
        return documents

    for file_path in sorted(directory.glob("*.txt")):
        text = _read_text_file(file_path)
        if not text:
            continue
        documents.append(
            {
                "source_file": str(file_path),
                "text": text,
            }
        )
    return documents


def load_selected_txt_documents(file_paths: List[str]) -> List[Dict[str, str]]:
    documents: List[Dict[str, str]] = []
    for file_name in file_paths:
        file_path = Path(file_name)
        if file_path.suffix.lower() != ".txt" or not file_path.exists():
            continue
        text = _read_text_file(file_path)
        if not text:
            continue
        documents.append(
            {
                "source_file": str(file_path),
                "text": text,
            }
        )
    return documents
