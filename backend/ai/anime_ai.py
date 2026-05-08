from __future__ import annotations

from typing import List, Tuple

from backend.ai.judge_ai import judge_related_conversation
from backend.services.gpt_client import generate_chat_answer
from backend.services.rag_engine import get_rag_payload


ANIME_SYSTEM_PROMPT = """
당신은 애니 토론, 추천, 설명을 도와주는 대화형 AI입니다.

답변 원칙:
- 서버가 시작될 때 미리 읽어둔 anime_notes 참고 내용 안에서 우선 답변하세요.
- 참고 내용이 있으면 그 범위 안에서 설명하고, 없는 내용을 아는 척하지 마세요.
- 감정 표현이 들어오면 작품, 캐릭터, 장면, 전개 이야기로 자연스럽게 이어 가세요.
- 단순 설명만 하지 말고 토론, 추천, 해석을 상황에 맞게 섞으세요.
- 대화를 이어 갈 수 있도록 마지막에 질문이나 다음 관점을 덧붙이세요.

말투:
- 자연스럽고 부드러운 한국어
- 친근하지만 과하게 가볍지 않은 톤
""".strip()


def generate_anime_answer(message: str, history: List[dict] | None = None) -> Tuple[str, List[str]]:
    rag_payload = get_rag_payload(domain="anime", query=message)
    answer = generate_chat_answer(
        domain="anime",
        question=message,
        context=rag_payload["context"],
        history=history,
        system_prompt=ANIME_SYSTEM_PROMPT,
    )
    return answer, rag_payload["sources"]


def handle_anime_chat(message: str, history: List[dict] | None = None) -> Tuple[str, List[str]]:
    judgement = judge_related_conversation(domain="anime", message=message, history=history)
    if not judgement.get("related"):
        return judgement.get("message", ""), []
    return generate_anime_answer(message=message, history=history)
