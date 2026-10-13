"""연락처(contacts.json)와 마지막 연락일(state.json) 관리."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

RELATIONS = {"family": "가족", "friend": "친구"}


@dataclass
class Contact:
    id: str
    name: str
    phone: str
    relation: str = "friend"  # "family" | "friend"
    call_name: str = ""  # 문자 첫머리에 부를 호칭 (예: "엄마", "민수야")
    polite: bool = False  # True면 존댓말
    notes: str = ""  # 근황 메모 (AI 생성 시 참고)
    every_days: int = 7  # 이 주기마다 안부를 묻고 싶음
    last_sent: date | None = field(default=None)

    def __post_init__(self) -> None:
        if self.relation not in RELATIONS:
            raise ValueError(f"{self.name}: relation은 family 또는 friend여야 합니다")
        if not self.call_name:
            self.call_name = self.name

    def days_since(self, today: date) -> int | None:
        return None if self.last_sent is None else (today - self.last_sent).days

    def is_due(self, today: date) -> bool:
        since = self.days_since(today)
        return since is None or since >= self.every_days

    def to_dict(self, today: date) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "relation": self.relation,
            "relation_label": RELATIONS[self.relation],
            "call_name": self.call_name,
            "polite": self.polite,
            "every_days": self.every_days,
            "last_sent": self.last_sent.isoformat() if self.last_sent else None,
            "days_since": self.days_since(today),
            "due": self.is_due(today),
        }


class ContactBook:
    def __init__(self, contacts_path: Path, state_path: Path) -> None:
        self.contacts_path = contacts_path
        self.state_path = state_path
        self.contacts: dict[str, Contact] = {}
        self.reload()

    def reload(self) -> None:
        raw = json.loads(self.contacts_path.read_text(encoding="utf-8"))
        state = self._read_state()
        contacts = {}
        for item in raw:
            c = Contact(**item)
            if c.id in contacts:
                raise ValueError(f"중복된 id: {c.id}")
            if c.id in state:
                c.last_sent = date.fromisoformat(state[c.id])
            contacts[c.id] = c
        self.contacts = contacts

    def get(self, contact_id: str) -> Contact:
        return self.contacts[contact_id]

    def ordered(self, today: date) -> list[Contact]:
        """연락할 때가 된 사람 → 오래 연락 안 한 사람 순."""
        def key(c: Contact):
            since = c.days_since(today)
            overdue = 10**6 if since is None else since - c.every_days
            return (not c.is_due(today), -overdue, c.name)

        return sorted(self.contacts.values(), key=key)

    def mark_sent(self, contact_id: str, when: date) -> None:
        self.get(contact_id).last_sent = when
        state = self._read_state()
        state[contact_id] = when.isoformat()
        self.state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _read_state(self) -> dict[str, str]:
        if not self.state_path.exists():
            return {}
        return json.loads(self.state_path.read_text(encoding="utf-8"))
