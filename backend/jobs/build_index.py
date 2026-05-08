from __future__ import annotations

import uuid
from pathlib import Path
from typing import Dict, List

from backend.config import settings
from backend.services.document_loader import load_txt_documents
from backend.services.embedding_service import create_embedding
from backend.services.file_checker import build_current_hashes, load_saved_hashes, save_hashes
from backend.services.index_cache import set_cached_index
from backend.services.text_splitter import split_documents
from backend.services.vector_store import save_index


DOMAIN_CONFIG = {
    "anime": (settings.ANIME_NOTES_DIR, settings.ANIME_INDEX_DIR),
    "drama": (settings.DRAMA_NOTES_DIR, settings.DRAMA_INDEX_DIR),
}


def _build_domain_chunks(note_dir: Path) -> List[Dict]:
    documents = load_txt_documents(note_dir)
    chunks: List[Dict] = []
    for chunk in split_documents(
        documents,
        chunk_size=settings.CHUNK_SIZE,
        overlap=settings.CHUNK_OVERLAP,
    ):
        chunks.append(
            {
                "id": str(uuid.uuid4()),
                "source_file": chunk["source_file"],
                "text": chunk["text"],
                "embedding": create_embedding(chunk["text"]),
            }
        )
    return chunks


def build_domain_index(domain: str) -> List[Dict]:
    note_dir, index_dir = DOMAIN_CONFIG[domain]
    chunks = _build_domain_chunks(note_dir)
    save_index(index_dir, chunks)
    set_cached_index(domain, chunks)

    all_hashes = load_saved_hashes(settings.FILE_HASH_PATH)
    all_hashes[domain] = build_current_hashes(note_dir)
    save_hashes(settings.FILE_HASH_PATH, all_hashes)
    return chunks


def build_all_indexes() -> None:
    for domain in DOMAIN_CONFIG:
        build_domain_index(domain)
