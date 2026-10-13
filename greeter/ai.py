"""Claude API로 상대방 근황에 맞춘 안부 문자를 생성 (선택 기능).

ANTHROPIC_API_KEY(또는 `ant auth login` 프로필)가 있고 `anthropic` 패키지가
설치되어 있을 때만 사용됩니다. 그렇지 않으면 templates.py로 대체됩니다.
"""
from __future__ import annotations

import os
from datetime import datetime

from .contacts import RELATIONS, Contact

MODEL = os.environ.get("GREETER_MODEL", "claude-opus-5-5")

SYSTEM = """당신은 사용자가 가까운 가족·친구에게 보낼 안부 문자를 대신 써 주는 도우미입니다.
- 사용자 본인이 직접 쓴 것처럼 자연스러운 한국어 문자 한 통만 출력하세요. 따옴표, 설명, 선택지는 넣지 마세요.
- 2~4문장, 150자 이내로 짧고 따뜻하게. 이모지는 0~1개.
- 지정된 말투(존댓말/반말)와 호칭을 반드시 지키세요.
- 근황 메모가 있으면 자연스럽게 한 번만 언급하되, 메모에 없는 사실을 지어내지 마세요."""


class AIUnavailable(RuntimeError):
    pass


def _client():
    try:
        import anthropic
    except ImportError as e:
        raise AIUnavailable("anthropic 패키지가 설치되어 있지 않습니다 (pip install anthropic)") from e
    try:
        return anthropic.Anthropic()
    except anthropic.AnthropicError as e:
        raise AIUnavailable(f"Claude API 인증 정보를 찾을 수 없습니다: {e}") from e


def build_prompt(contact: Contact, now: datetime, previous: str | None = None) -> str:
    lines = [
        f"받는 사람: {contact.name} ({RELATIONS[contact.relation]})",
        f"호칭: {contact.call_name}",
        f"말투: {'존댓말' if contact.polite else '반말'}",
        f"지금: {now:%Y-%m-%d %H시}",
    ]
    if contact.notes:
        lines.append(f"근황 메모: {contact.notes}")
    if previous:
        lines.append(f"이전 초안과는 다른 표현으로 써 주세요: {previous}")
    return "\n".join(lines)


def generate(contact: Contact, now: datetime, previous: str | None = None) -> str:
    client = _client()
    import anthropic

    try:
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=SYSTEM,
            output_config={"effort": "low"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            messages=[{"role": "user", "content": build_prompt(contact, now, previous)}],
        )
    except TypeError as e:
        # 키/프로필이 전혀 없으면 SDK가 요청 시점에 TypeError를 던짐
        if "authentication" not in str(e):
            raise
        raise AIUnavailable("Claude API 키가 설정되어 있지 않습니다 (ANTHROPIC_API_KEY)") from e
    except anthropic.AuthenticationError as e:
        raise AIUnavailable("Claude API 키가 올바르지 않습니다") from e
    except anthropic.APIConnectionError as e:
        raise AIUnavailable("Claude API에 연결할 수 없습니다") from e
    except anthropic.APIStatusError as e:
        raise AIUnavailable(f"Claude API 오류 ({e.status_code})") from e

    if response.stop_reason == "refusal":
        raise AIUnavailable("Claude가 이 요청에 대한 응답을 거절했습니다")
    text = "".join(b.text for b in response.content if b.type == "text").strip()
    if not text:
        raise AIUnavailable("Claude가 빈 응답을 돌려줬습니다")
    return text.strip('"“”')
