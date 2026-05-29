from __future__ import annotations

from typing import List, Tuple

from backend.ai.judge_ai import judge_related_conversation
from backend.services.gpt_client import generate_chat_answer
from backend.services.rag_engine import get_rag_payload


DRAMA_SYSTEM_PROMPT = """
당신은 드라마 토론, 추천, 설명을 도와주는 대화형 AI입니다.

응답 지침:
- 사용자의 질문과 감상을 기준으로 드라마 대화를 자연스럽게 이어가세요.
- 참고 문맥이 있으면 그 범위 안에서 설명하고, 없는 정보는 지어내지 마세요.
- 작품, 인물, 전개, 결말, 연출, 메시지를 상황에 맞게 다루세요.
- 일반 모드에서는 설명, 추천, 가벼운 대화, 작품 정보 제공을 자연스럽게 섞으세요.
- 마지막에는 대화를 이어갈 만한 짧은 질문이나 비교 포인트를 덧붙여도 좋습니다.

말투:
- 부드럽고 자연스러운 한국어
- 과하게 장황하지 않은 대화형 톤
""".strip()

DRAMA_DISCUSSION_APPENDIX = """
현재 모드는 discussion입니다.

토론 모드 지침:
- 사용자의 의견에 동의, 반박, 보완을 자연스럽게 섞으세요.
- 작품, 인물, 전개, 결말, 연출, 메시지에 대해 근거를 요구하거나 다른 해석을 제시하세요.
- 단순 추천이나 요약으로 끝내지 말고, 사람과 토론하듯 논점을 이어가세요.
- 공격적이거나 비꼬는 태도는 피하고, 차분하게 관점을 비교하세요.
""".strip()


def _build_drama_system_prompt(mode: str) -> str:
    if mode == "discussion":
        return f"{DRAMA_SYSTEM_PROMPT}\n\n{DRAMA_DISCUSSION_APPENDIX}"
    return DRAMA_SYSTEM_PROMPT


def generate_drama_answer(
    message: str,
    mode: str = "normal",
    history: List[dict] | None = None,
) -> Tuple[str, List[str]]:
    rag_payload = get_rag_payload(domain="drama", query=message)
    answer = generate_chat_answer(
        domain="drama",
        question=message,
        context=rag_payload["context"],
        history=history,
        system_prompt=_build_drama_system_prompt(mode),
    )
    return answer, rag_payload["sources"]


def handle_drama_chat(
    message: str,
    mode: str = "normal",
    history: List[dict] | None = None,
) -> Tuple[str, List[str]]:
    judgement = judge_related_conversation(
        domain="drama",
        message=message,
        mode=mode,
        history=history,
    )
    if not judgement.get("related"):
        return judgement.get("message", ""), []
    return generate_drama_answer(message=message, mode=mode, history=history)
