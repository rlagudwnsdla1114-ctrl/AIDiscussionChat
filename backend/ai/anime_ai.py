from __future__ import annotations

from typing import List, Tuple

from backend.ai.judge_ai import judge_related_conversation
from backend.services.gpt_client import generate_chat_answer
from backend.services.rag_engine import get_rag_payload


ANIME_SYSTEM_PROMPT = """
당신은 애니 토론, 추천, 설명을 도와주는 대화형 AI입니다.

응답 지침:
- 사용자가 던진 질문과 감상을 기준으로 애니 대화를 자연스럽게 이어가세요.
- 참고 문맥이 있으면 그 범위 안에서 설명하고, 없는 정보는 단정하지 마세요.
- 작품, 캐릭터, 작화, 전개, 결말, 설정을 상황에 맞게 다루세요.
- 일반 모드에서는 설명, 추천, 가벼운 대화, 작품 정보 제공을 자연스럽게 섞으세요.
- 마지막에는 대화를 이어갈 만한 짧은 질문이나 비교 포인트를 덧붙여도 좋습니다.

말투:
- 자연스럽고 부드러운 한국어
- 과하게 장황하지 않은 대화형 톤
""".strip()

ANIME_DISCUSSION_APPENDIX = """
현재 모드는 discussion입니다.

토론 모드 지침:
- 사용자의 의견을 그대로 받아들이기만 하지 말고, 필요하면 반박하거나 다른 관점을 제시하세요.
- 작품, 캐릭터, 전개, 결말, 연출, 설정에 대해 근거를 묻거나 비교 질문을 던지세요.
- 단순 추천이나 요약으로 끝내지 말고, 논점을 좁혀가며 토론을 이어가세요.
- 공격적이거나 비꼬는 태도는 피하고, 사람과 토론하듯 차분하고 선명하게 말하세요.
""".strip()


def _build_anime_system_prompt(mode: str) -> str:
    if mode == "discussion":
        return f"{ANIME_SYSTEM_PROMPT}\n\n{ANIME_DISCUSSION_APPENDIX}"
    return ANIME_SYSTEM_PROMPT


def generate_anime_answer(
    message: str,
    mode: str = "normal",
    history: List[dict] | None = None,
) -> Tuple[str, List[str]]:
    rag_payload = get_rag_payload(domain="anime", query=message)
    answer = generate_chat_answer(
        domain="anime",
        question=message,
        context=rag_payload["context"],
        history=history,
        system_prompt=_build_anime_system_prompt(mode),
    )
    return answer, rag_payload["sources"]


def handle_anime_chat(
    message: str,
    mode: str = "normal",
    history: List[dict] | None = None,
) -> Tuple[str, List[str]]:
    judgement = judge_related_conversation(
        domain="anime",
        message=message,
        mode=mode,
        history=history,
    )
    if not judgement.get("related"):
        return judgement.get("message", ""), []
    return generate_anime_answer(message=message, mode=mode, history=history)
