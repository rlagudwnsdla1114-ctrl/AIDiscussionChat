from __future__ import annotations

import json
from typing import List

from openai import OpenAI

from backend.config import settings


def _client() -> OpenAI | None:
    if not settings.OPENAI_API_KEY:
        return None
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def _chat_completion(
    *,
    messages: List[dict],
    temperature: float,
    response_format: dict | None = None,
) -> str:
    client = _client()
    if client is None:
        raise RuntimeError("OpenAI client is unavailable.")

    request_args = {
        "model": settings.GPT_MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    if response_format is not None:
        request_args["response_format"] = response_format

    response = client.chat.completions.create(**request_args)
    return (response.choices[0].message.content or "").strip()


def _fallback_answer(domain: str, question: str, context: str) -> str:
    domain_hint = "애니 이야기" if domain == "anime" else "드라마 이야기"
    if context:
        return (
            f"지금 참고 메모를 바탕으로 보면 {domain_hint}로 이어서 이야기할 수 있어 보여. "
            f"'{question}'에서 특히 어떤 작품이나 장면이 떠올랐는지 말해주면 더 구체적으로 같이 이야기해볼게."
        )
    return (
        f"지금은 참고 메모가 많지 않지만 {domain_hint} 쪽으로는 계속 이야기할 수 있어. "
        f"'{question}'라고 느낀 이유가 전개 때문인지, 캐릭터 때문인지 말해주면 거기서부터 이어가볼게."
    )


def _build_messages(
    system_prompt: str,
    question: str,
    context: str,
    history: List[dict] | None,
) -> List[dict]:
    messages: List[dict] = [{"role": "system", "content": system_prompt}]

    if context:
        messages.append(
            {
                "role": "system",
                "content": f"아래는 서버 시작 시 미리 읽어둔 참고 메모입니다.\n{context}",
            }
        )

    for item in history or []:
        if item.get("role") in {"user", "assistant"} and item.get("content"):
            messages.append({"role": item["role"], "content": item["content"]})

    messages.append({"role": "user", "content": question})
    return messages


def generate_chat_answer(
    *,
    domain: str,
    question: str,
    context: str,
    history: List[dict] | None,
    system_prompt: str,
) -> str:
    if _client() is None:
        return _fallback_answer(domain, question, context)

    try:
        answer = _chat_completion(
            messages=_build_messages(system_prompt, question, context, history),
            temperature=0.8,
        )
        return answer.strip() or _fallback_answer(domain, question, context)
    except Exception:
        return _fallback_answer(domain, question, context)


def generate_json_answer(
    *,
    system_prompt: str,
    user_prompt: str,
    fallback_payload: dict,
) -> dict:
    if _client() is None:
        return fallback_payload

    try:
        content = _chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        payload = json.loads(content)
        if isinstance(payload, dict):
            return payload
    except Exception:
        pass
    return fallback_payload
