from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = BASE_DIR / "backend"
DATA_DIR = BACKEND_DIR / "data"
ANIME_NOTES_DIR = DATA_DIR / "anime_notes"
DRAMA_NOTES_DIR = DATA_DIR / "drama_notes"
INDEXES_DIR = BACKEND_DIR / "indexes"
ANIME_INDEX_DIR = INDEXES_DIR / "anime"
DRAMA_INDEX_DIR = INDEXES_DIR / "drama"
STORAGE_DIR = BACKEND_DIR / "storage"
FILE_HASH_PATH = STORAGE_DIR / "file_hashes.json"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4.1-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
TOP_K = int(os.getenv("TOP_K", "5"))

for path in (
    BACKEND_DIR,
    DATA_DIR,
    ANIME_NOTES_DIR,
    DRAMA_NOTES_DIR,
    INDEXES_DIR,
    ANIME_INDEX_DIR,
    DRAMA_INDEX_DIR,
    STORAGE_DIR,
):
    path.mkdir(parents=True, exist_ok=True)
