from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from backend.config import settings
from backend.services.embedding_service import cosine_similarity, create_embedding, keyword_score
from backend.services.index_cache import get_cached_index


DOMAIN_INDEX_DIRS = {
    "anime": settings.ANIME_INDEX_DIR,
    "drama": settings.DRAMA_INDEX_DIR,
}


def _resolve_index_dir(domain: str) -> Path:
    return DOMAIN_INDEX_DIRS[domain]


def search_relevant_chunks(domain: str, query: str, top_k: int | None = None) -> List[Dict]:
    _resolve_index_dir(domain)
    chunks = get_cached_index(domain)
    if not chunks:
        return []

    top_k = top_k or settings.TOP_K
    query_embedding = create_embedding(query)
    scored_chunks: List[Dict] = []

    for chunk in chunks:
        embedding = chunk.get("embedding") or []
        if query_embedding and embedding and len(query_embedding) == len(embedding):
            score = cosine_similarity(query_embedding, embedding)
        else:
            score = keyword_score(query, chunk.get("text", ""))
        scored_chunks.append({**chunk, "score": score})

    scored_chunks.sort(key=lambda item: item["score"], reverse=True)
    return [chunk for chunk in scored_chunks[:top_k] if chunk["score"] > 0]


def build_context(chunks: List[Dict]) -> str:
    if not chunks:
        return ""

    context_parts = []
    for chunk in chunks:
        context_parts.append(
            f"[출처: {chunk['source_file']}]\n{chunk['text']}"
        )
    return "\n\n".join(context_parts)


def get_rag_payload(domain: str, query: str, top_k: int | None = None) -> Dict:
    chunks = search_relevant_chunks(domain=domain, query=query, top_k=top_k)
    return {
        "context": build_context(chunks),
        "sources": sorted({chunk["source_file"] for chunk in chunks}),
        "chunks": chunks,
    }
