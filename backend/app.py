from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.anime_routes import router as anime_router
from backend.api.drama_routes import router as drama_router
from backend.jobs.update_index import prepare_indexes
from backend.services.index_cache import load_indexes_into_memory


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Example run command:
    # uvicorn backend.app:app --reload
    prepare_indexes()
    load_indexes_into_memory()
    yield


app = FastAPI(title="DebateMind API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(anime_router)
app.include_router(drama_router)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
