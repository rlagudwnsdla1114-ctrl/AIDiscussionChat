from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable


def calculate_file_hash(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_saved_hashes(hash_path: Path) -> Dict[str, Dict[str, str]]:
    if not hash_path.exists():
        return {}
    try:
        return json.loads(hash_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_hashes(hash_path: Path, data: Dict[str, Dict[str, str]]) -> None:
    hash_path.parent.mkdir(parents=True, exist_ok=True)
    hash_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_current_hashes(note_dir: Path) -> Dict[str, str]:
    if not note_dir.exists():
        return {}
    return {
        str(file_path): calculate_file_hash(file_path)
        for file_path in sorted(note_dir.glob("*.txt"))
    }


def detect_file_changes(
    previous_hashes: Dict[str, str],
    current_hashes: Dict[str, str],
) -> Dict[str, Iterable[str]]:
    previous_files = set(previous_hashes.keys())
    current_files = set(current_hashes.keys())

    added = sorted(current_files - previous_files)
    deleted = sorted(previous_files - current_files)
    modified = sorted(
        file_path
        for file_path in current_files & previous_files
        if previous_hashes[file_path] != current_hashes[file_path]
    )

    return {
        "added": added,
        "modified": modified,
        "deleted": deleted,
        "has_changes": bool(added or modified or deleted),
    }
