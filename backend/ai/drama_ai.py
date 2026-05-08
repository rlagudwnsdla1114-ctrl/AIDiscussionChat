from __future__ import annotations

from typing import List, Tuple

from backend.ai.judge_ai import judge_related_conversation
from backend.services.gpt_client import generate_chat_answer
from backend.services.rag_engine import get_rag_payload


DRAMA_SYSTEM_PROMPT = """
당신은 드라마 토론, 추천, 설명을 도와주는 대화형 AI입니다.

답변 원칙:
- 서버가 시작될 때 미리 읽어둔 drama_notes 참고 내용 안에서 우선 답변하세요.
- 참고 내용이 있으면 그 범위 안에서 설명하고, 없는 정보는 추측해서 단정하지 마세요.
- 감정 표현이 들어오면 인물 행동, 관계, 장면, 전개 이야기로 자연스럽게 이어 가세요.
- 단순 정보 나열보다 대화 흐름을 만들고, 필요하면 추천과 해석을 함께 제시하세요.
- 답변 끝에는 사용자가 더 말할 수 있도록 질문이나 관점을 덧붙이세요.

말투:
- 부드럽고 사람 같은 한국어
- 친근하지만 정리된 톤
""".strip()


def generate_drama_answer(message: str, history: List[dict] | None = None) -> Tuple[str, List[str]]:
    rag_payload = get_rag_payload(domain="drama", query=message)
    answer = generate_chat_answer(
        domain="drama",
        question=message,
        context=rag_payload["context"],
        history=history,
        system_prompt=DRAMA_SYSTEM_PROMPT,
    )
    return answer, rag_payload["sources"]


def handle_drama_chat(message: str, history: List[dict] | None = None) -> Tuple[str, List[str]]:
    judgement = judge_related_conversation(domain="drama", message=message, history=history)
    if not judgement.get("related"):
        return judgement.get("message", ""), []
    return generate_drama_answer(message=message, history=history)
