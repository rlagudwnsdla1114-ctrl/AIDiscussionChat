from __future__ import annotations

from typing import List

from backend.services.gpt_client import generate_json_answer


OUT_OF_SCOPE_MESSAGE = (
    "이 서비스는 애니와 드라마에 대한 토론, 추천, 설명을 위한 서비스입니다. "
    "애니 또는 드라마 관련 이야기를 해주세요."
)

JUDGE_SYSTEM_PROMPT = """
You are a classifier for an anime/drama chat service.
Return JSON only.

Decide whether the user's message is related to the current chat room domain.
- domain=anime: anime discussion, recommendation, explanation, titles, characters, scenes, plot, ending, directing, worldbuilding, themes, or emotions that can naturally continue into anime conversation => related true
- domain=drama: drama discussion, recommendation, explanation, titles, characters, scenes, plot, ending, directing, themes, messages, or emotions that can naturally continue into drama conversation => related true
- Generic unrelated talk like food, coding help, errands, and off-topic requests => related false
- If the user explicitly denies the topic such as "애니 얘기 아니야" or "드라마 얘기 아니야", return false
- Ambiguous emotional messages should be judged generously based on the current domain
- If mode=discussion, also consider whether the message can become a debate topic about the domain even when it is phrased as an opinion, criticism, comparison, or interpretation

True JSON shape:
{"related": true, "reason": "..."}

False JSON shape:
{"related": false, "message": "이 서비스는 애니와 드라마에 대한 토론, 추천, 설명을 위한 서비스입니다. 애니 또는 드라마 관련 이야기를 해주세요."}
""".strip()

NEGATIVE_PHRASES = {
    "애니 얘기 아니야",
    "드라마 얘기 아니야",
}

RELATED_KEYWORDS = {
    "anime": [
        "애니",
        "애니메이션",
        "만화",
        "캐릭터",
        "장면",
        "전개",
        "결말",
        "추천",
        "볼 거",
        "작품",
        "설정",
        "연출",
    ],
    "drama": [
        "드라마",
        "등장인물",
        "인물",
        "장면",
        "전개",
        "결말",
        "추천",
        "볼 거",
        "작품",
        "메시지",
        "연출",
    ],
}

EMOTIONAL_KEYWORDS = [
    "힘들",
    "답답",
    "슬프",
    "짜증",
    "화나",
    "열받",
    "설레",
    "우울",
    "무섭",
    "재밌",
    "재미없",
]

DISCUSSION_KEYWORDS = [
    "과대평가",
    "저평가",
    "별로",
    "억지",
    "이해 안",
    "납득",
    "왜",
    "vs",
    "비교",
    "반박",
    "토론",
]


def _fallback_judgement(domain: str, message: str, mode: str = "normal") -> dict:
    text = message.strip().lower()
    if not text:
        return {"related": False, "message": OUT_OF_SCOPE_MESSAGE}

    if text in NEGATIVE_PHRASES:
        return {"related": False, "message": OUT_OF_SCOPE_MESSAGE}

    if any(keyword in text for keyword in RELATED_KEYWORDS[domain]):
        return {
            "related": True,
            "reason": f"The message directly matches the {domain} room topic.",
        }

    if any(keyword in text for keyword in EMOTIONAL_KEYWORDS):
        return {
            "related": True,
            "reason": f"The emotional message can naturally continue into {domain} discussion.",
        }

    if mode == "discussion" and any(keyword in text for keyword in DISCUSSION_KEYWORDS):
        return {
            "related": True,
            "reason": f"The message can continue as a {domain} debate topic.",
        }

    return {"related": False, "message": OUT_OF_SCOPE_MESSAGE}


def judge_related_conversation(
    *,
    domain: str,
    message: str,
    mode: str = "normal",
    history: List[dict] | None = None,
) -> dict:
    history_lines = []
    for item in history or []:
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and content:
            history_lines.append(f"{role}: {content}")

    user_prompt = (
        f"domain: {domain}\n"
        f"mode: {mode}\n"
        f"recent_history:\n{chr(10).join(history_lines) if history_lines else '(none)'}\n\n"
        f"user_message:\n{message}"
    )
    fallback_payload = _fallback_judgement(domain, message, mode)
    result = generate_json_answer(
        domain=domain,
        system_prompt=JUDGE_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        fallback_payload=fallback_payload,
    )

    if result.get("related") is True and isinstance(result.get("reason"), str):
        return {"related": True, "reason": result["reason"]}
    if result.get("related") is False and isinstance(result.get("message"), str):
        return {"related": False, "message": result["message"]}
    return fallback_payload
