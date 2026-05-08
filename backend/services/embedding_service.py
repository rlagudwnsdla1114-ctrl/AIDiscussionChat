from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable, List, Optional

from openai import OpenAI

from backend.config import settings


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[0-9A-Za-z가-힣]{2,}", text.lower())


def _local_embedding(text: str) -> List[float]:
    counts = Counter(_tokenize(text))
    if not counts:
        return []

    tokens = sorted(counts.keys())[:64]
    total = sum(counts.values()) or 1
    vector = [counts[token] / total for token in tokens]
    return vector


def has_openai_key() -> bool:
    return bool(settings.OPENAI_API_KEY)


def _client() -> Optional[OpenAI]:
    if not has_openai_key():
        return None
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def create_embedding(text: str) -> List[float]:
    client = _client()
    if client is None:
        return _local_embedding(text)

    try:
        response = client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text,
        )
        return list(response.data[0].embedding)
    except Exception:
        return _local_embedding(text)


def create_embeddings(texts: Iterable[str]) -> List[List[float]]:
    return [create_embedding(text) for text in texts]


def cosine_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    if not vector_a or not vector_b or len(vector_a) != len(vector_b):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    return dot_product / (magnitude_a * magnitude_b)


def keyword_score(query: str, text: str) -> float:
    query_tokens = set(_tokenize(query))
    text_tokens = Counter(_tokenize(text))
    if not query_tokens:
        return 0.0
    return float(sum(text_tokens[token] for token in query_tokens))
