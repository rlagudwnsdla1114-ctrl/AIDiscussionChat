from __future__ import annotations

from typing import List

from backend.services.gpt_client import generate_json_answer


OUT_OF_SCOPE_MESSAGE = (
    "\uc774 \uc11c\ube44\uc2a4\ub294 \uc560\ub2c8\uc640 \ub4dc\ub77c\ub9c8\uc5d0 \ub300\ud55c \ud1a0\ub860, "
    "\ucd94\ucc9c, \uc124\uba85\uc744 \uc704\ud55c \uc11c\ube44\uc2a4\uc785\ub2c8\ub2e4. "
    "\uc560\ub2c8 \ub610\ub294 \ub4dc\ub77c\ub9c8 \uad00\ub828 \uc774\uc57c\uae30\ub97c \ud574\uc8fc\uc138\uc694."
)

JUDGE_SYSTEM_PROMPT = """
You are a classifier for an anime/drama chat service.
Return JSON only.

Decide whether the user's message is related to the current chat room domain.
- domain=anime: anime discussion, recommendation, explanation, titles, characters, scenes, plot, ending, or emotion that can naturally continue into anime conversation => related true
- domain=drama: drama discussion, recommendation, explanation, titles, characters, scenes, plot, ending, or emotion that can naturally continue into drama conversation => related true
- Generic unrelated talk like food, coding help, errands, and off-topic requests => related false
- If the user explicitly denies the topic like "애니 얘기 아니야" or "드라마 얘기 아니야", return false
- Ambiguous emotional messages should be judged generously based on the current domain

True JSON shape:
{"related": true, "reason": "..."}

False JSON shape:
{"related": false, "message": "이 서비스는 애니와 드라마에 대한 토론, 추천, 설명을 위한 서비스입니다. 애니 또는 드라마 관련 이야기를 해주세요."}
""".strip()

NEGATIVE_PHRASES = {
    "\uc560\ub2c8 \uc598\uae30 \uc544\ub2c8\uc57c",
    "\ub4dc\ub77c\ub9c8 \uc598\uae30 \uc544\ub2c8\uc57c",
}

RELATED_KEYWORDS = {
    "anime": [
        "\uc560\ub2c8",
        "\uc560\ub2c8\uba54",
        "\ub9cc\ud654",
        "\uce90\ub9ad\ud130",
        "\uc7a5\uba74",
        "\uc804\uac1c",
        "\uacb0\ub9d0",
        "\ucd94\ucc9c",
        "\ubcfc \uac70",
        "\uc791\ud488",
    ],
    "drama": [
        "\ub4dc\ub77c\ub9c8",
        "\ub4f1\uc7a5\uc778\ubb3c",
        "\uc778\ubb3c",
        "\uc7a5\uba74",
        "\uc804\uac1c",
        "\uacb0\ub9d0",
        "\ucd94\ucc9c",
        "\ubcfc \uac70",
        "\uc791\ud488",
    ],
}

EMOTIONAL_KEYWORDS = [
    "\ud798\ub4e4",
    "\ub2f5\ub2f5",
    "\uc2ac\ud504",
    "\uc9dc\uc99d",
    "\ud654\ub098",
    "\uc5f4\ubc1b",
    "\uc124\ub808",
    "\uc6b0\uc6b8",
    "\ubb34\uc11d",
    "\uc7ac\ubc0c",
    "\uc7ac\ubbf8\uc5c6",
]


def _fallback_judgement(domain: str, message: str) -> dict:
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

    return {"related": False, "message": OUT_OF_SCOPE_MESSAGE}


def judge_related_conversation(
    *,
    domain: str,
    message: str,
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
        f"recent_history:\n{chr(10).join(history_lines) if history_lines else '(none)'}\n\n"
        f"user_message:\n{message}"
    )
    fallback_payload = _fallback_judgement(domain, message)
    result = generate_json_answer(
        system_prompt=JUDGE_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        fallback_payload=fallback_payload,
    )

    if result.get("related") is True and isinstance(result.get("reason"), str):
        return {"related": True, "reason": result["reason"]}
    if result.get("related") is False and isinstance(result.get("message"), str):
        return {"related": False, "message": result["message"]}
    return fallback_payload
