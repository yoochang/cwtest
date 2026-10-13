"""API 키 없이도 동작하는 규칙 기반 안부 문자 생성기.

계절·시간대·관계(가족/친구)·말투(존댓말/반말)에 맞춰 문장을 조합합니다.
"""
from __future__ import annotations

import random
from datetime import datetime

from .contacts import Contact

# (반말, 존댓말) 쌍
SEASON = {
    "spring": [
        ("요즘 날씨 많이 풀렸더라.", "요즘 날씨가 많이 풀렸어요."),
        ("꽃 피는 거 보니까 생각나서 연락해.", "꽃 피는 걸 보니 생각나서 연락드려요."),
    ],
    "summer": [
        ("요즘 너무 덥지? 더위 안 먹게 조심해.", "요즘 많이 덥죠? 더위 드시지 않게 조심하세요."),
        ("장마라 습한데 잘 지내고 있어?", "장마라 습한데 잘 지내고 계세요?"),
    ],
    "autumn": [
        ("날이 선선해졌네. 환절기 감기 조심해.", "날이 선선해졌어요. 환절기 감기 조심하세요."),
        ("가을 하늘 보니까 생각나서 연락해.", "가을 하늘을 보니 생각나서 연락드려요."),
    ],
    "winter": [
        ("요즘 많이 춥지? 따뜻하게 입고 다녀.", "요즘 많이 춥죠? 따뜻하게 입고 다니세요."),
        ("추운데 감기 안 걸렸어?", "추운데 감기는 안 걸리셨어요?"),
    ],
}

TIME = {
    "morning": [("좋은 아침!", "좋은 아침이에요!")],
    "afternoon": [("점심은 잘 먹었어?", "점심은 맛있게 드셨어요?")],
    "evening": [("오늘 하루도 고생 많았어.", "오늘 하루도 고생 많으셨어요.")],
    "night": [("늦은 시간인데 잘 자고 있으려나.", "늦은 시간이라 푹 쉬고 계시길 바라요.")],
}

ASK = {
    "family": [
        ("요즘 건강은 괜찮아? 밥 잘 챙겨 먹고.", "요즘 건강은 괜찮으세요? 식사 잘 챙겨 드세요."),
        ("별일 없지? 다들 잘 지내?", "별일 없으시죠? 다들 잘 지내시죠?"),
    ],
    "friend": [
        ("요즘 어떻게 지내? 별일 없지?", "요즘 어떻게 지내세요? 별일 없으시죠?"),
        ("바쁘게 지내지? 무리하지 말고.", "많이 바쁘시죠? 무리하지 마세요."),
    ],
}

CLOSE = {
    "family": [
        ("조만간 얼굴 보러 갈게. 사랑해!", "조만간 찾아뵐게요. 사랑해요!"),
        ("시간 날 때 전화할게.", "시간 날 때 전화드릴게요."),
    ],
    "friend": [
        ("조만간 밥 한번 먹자!", "조만간 식사 한번 해요!"),
        ("시간 되면 연락 줘. 얼굴 보자!", "시간 되실 때 연락 주세요. 얼굴 봬요!"),
    ],
}


def season_of(month: int) -> str:
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    if month in (9, 10, 11):
        return "autumn"
    return "winter"


def time_of(hour: int) -> str:
    if 5 <= hour < 11:
        return "morning"
    if 11 <= hour < 17:
        return "afternoon"
    if 17 <= hour < 22:
        return "evening"
    return "night"


def generate(contact: Contact, now: datetime, rng: random.Random | None = None) -> str:
    rng = rng or random.Random()
    i = 1 if contact.polite else 0
    pick = lambda pool: rng.choice(pool)[i]  # noqa: E731

    greeting = f"{contact.call_name}, " if contact.polite else f"{contact.call_name}! "
    middle = pick(SEASON[season_of(now.month)]) if rng.random() < 0.6 else pick(
        TIME[time_of(now.hour)]
    )
    parts = [greeting + middle, pick(ASK[contact.relation]), pick(CLOSE[contact.relation])]
    return " ".join(parts)
