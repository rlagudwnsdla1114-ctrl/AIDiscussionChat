from __future__ import annotations

from fastapi import APIRouter

from backend.ai.anime_ai import handle_anime_chat
from backend.schemas.chat_schema import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/anime", tags=["anime"])


@router.post("/chat", response_model=ChatResponse)
def anime_chat(request: ChatRequest) -> ChatResponse:
    answer, sources = handle_anime_chat(
        message=request.message,
        history=[item.model_dump() for item in (request.history or [])],
    )
    return ChatResponse(answer=answer, sources=sources)
