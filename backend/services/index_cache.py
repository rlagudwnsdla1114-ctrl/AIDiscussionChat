from __future__ import annotations

from typing import Dict, List

from backend.config import settings
from backend.services.vector_store import load_index


_INDEX_CACHE: Dict[str, List[Dict]] = {
    "anime": [],
    "drama": [],
}


def load_indexes_into_memory() -> Dict[str, int]:
    _INDEX_CACHE["anime"] = load_index(settings.ANIME_INDEX_DIR)
    _INDEX_CACHE["drama"] = load_index(settings.DRAMA_INDEX_DIR)
    return {
        "anime": len(_INDEX_CACHE["anime"]),
        "drama": len(_INDEX_CACHE["drama"]),
    }


def get_cached_index(domain: str) -> List[Dict]:
    return list(_INDEX_CACHE.get(domain, []))


def set_cached_index(domain: str, chunks: List[Dict]) -> None:
    _INDEX_CACHE[domain] = list(chunks)
