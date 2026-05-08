from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class HistoryMessage(BaseModel):
    role: str = Field(..., description="user or assistant")
    content: str = Field(..., description="Chat message content")


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[HistoryMessage]] = None


class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = None
