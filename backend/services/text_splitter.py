from __future__ import annotations

from typing import Dict, List


def split_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 120,
    min_length: int = 80,
) -> List[str]:
    normalized = " ".join(text.split())
    if len(normalized) <= chunk_size:
        return [normalized] if len(normalized) >= min_length else []

    chunks: List[str] = []
    start = 0
    step = max(chunk_size - overlap, 1)

    while start < len(normalized):
        chunk = normalized[start : start + chunk_size].strip()
        if len(chunk) >= min_length:
            chunks.append(chunk)
        start += step

    return chunks


def split_documents(
    documents: List[Dict[str, str]],
    chunk_size: int = 800,
    overlap: int = 120,
) -> List[Dict[str, str]]:
    chunks: List[Dict[str, str]] = []
    for document in documents:
        for index, text in enumerate(split_text(document["text"], chunk_size, overlap)):
            chunks.append(
                {
                    "source_file": document["source_file"],
                    "chunk_index": index,
                    "text": text,
                }
            )
    return chunks
