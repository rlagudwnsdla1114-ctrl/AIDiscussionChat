from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


INDEX_FILE_NAME = "index.json"


def _index_path(index_dir: Path) -> Path:
    index_dir.mkdir(parents=True, exist_ok=True)
    return index_dir / INDEX_FILE_NAME


def load_index(index_dir: Path) -> List[Dict]:
    index_path = _index_path(index_dir)
    if not index_path.exists():
        return []
    try:
        return json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_index(index_dir: Path, chunks: List[Dict]) -> None:
    index_path = _index_path(index_dir)
    index_path.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def upsert_chunks(index_dir: Path, new_chunks: List[Dict]) -> List[Dict]:
    current_chunks = load_index(index_dir)
    replaced_files = {chunk["source_file"] for chunk in new_chunks}
    merged = [chunk for chunk in current_chunks if chunk["source_file"] not in replaced_files]
    merged.extend(new_chunks)
    save_index(index_dir, merged)
    return merged


def remove_chunks_by_source(index_dir: Path, source_files: List[str]) -> List[Dict]:
    current_chunks = load_index(index_dir)
    filtered = [chunk for chunk in current_chunks if chunk["source_file"] not in set(source_files)]
    save_index(index_dir, filtered)
    return filtered
