from __future__ import annotations

import uuid
from pathlib import Path
from typing import Dict, List

from backend.config import settings
from backend.jobs.build_index import DOMAIN_CONFIG, build_domain_index
from backend.services.document_loader import load_selected_txt_documents
from backend.services.embedding_service import create_embedding
from backend.services.file_checker import (
    build_current_hashes,
    detect_file_changes,
    load_saved_hashes,
    save_hashes,
)
from backend.services.index_cache import set_cached_index
from backend.services.text_splitter import split_documents
from backend.services.vector_store import load_index, save_index


def _build_chunks_for_files(file_paths: List[str]) -> List[Dict]:
    chunks: List[Dict] = []
    documents = load_selected_txt_documents(file_paths)
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


def update_domain_index(domain: str) -> Dict:
    note_dir, index_dir = DOMAIN_CONFIG[domain]
    saved_hashes = load_saved_hashes(settings.FILE_HASH_PATH)
    previous_hashes = saved_hashes.get(domain, {})
    current_hashes = build_current_hashes(note_dir)
    changes = detect_file_changes(previous_hashes, current_hashes)

    if not (index_dir / "index.json").exists():
        build_domain_index(domain)
        return {"domain": domain, "rebuilt": True, "changes": changes}

    if not changes["has_changes"]:
        return {"domain": domain, "rebuilt": False, "changes": changes}

    files_to_refresh = list(changes["added"]) + list(changes["modified"])
    files_to_remove = list(changes["modified"]) + list(changes["deleted"])

    current_chunks = load_index(index_dir)
    if files_to_remove:
        current_chunks = [chunk for chunk in current_chunks if chunk["source_file"] not in set(files_to_remove)]

    current_chunks.extend(_build_chunks_for_files(files_to_refresh))
    save_index(index_dir, current_chunks)
    set_cached_index(domain, current_chunks)

    saved_hashes[domain] = current_hashes
    save_hashes(settings.FILE_HASH_PATH, saved_hashes)
    return {"domain": domain, "rebuilt": False, "changes": changes}


def update_all_indexes() -> List[Dict]:
    return [update_domain_index(domain) for domain in DOMAIN_CONFIG]


def prepare_indexes() -> List[Dict]:
    return update_all_indexes()
