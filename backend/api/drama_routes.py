from __future__ import annotations

from fastapi import APIRouter

from backend.ai.drama_ai import handle_drama_chat
from backend.schemas.chat_schema import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/drama", tags=["drama"])


@router.post("/chat", response_model=ChatResponse)
def drama_chat(request: ChatRequest) -> ChatResponse:
    answer, sources = handle_drama_chat(
        message=request.message,
        history=[item.model_dump() for item in (request.history or [])],
    )
    return ChatResponse(answer=answer, sources=sources)
