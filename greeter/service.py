"""문자 초안 생성: AI가 가능하면 AI로, 아니면 템플릿으로."""
from __future__ import annotations

from datetime import datetime

from . import ai, templates
from .contacts import Contact


def draft(contact: Contact, now: datetime, use_ai: bool = True,
          previous: str | None = None) -> dict:
    if use_ai:
        try:
            return {"text": ai.generate(contact, now, previous), "source": "ai"}
        except ai.AIUnavailable as e:
            text = templates.generate(contact, now)
            return {"text": text, "source": "template", "warning": str(e)}
    return {"text": templates.generate(contact, now), "source": "template"}
