"""휴대폰 메시지 앱을 수신자·내용이 채워진 상태로 여는 sms: 링크 생성."""
from urllib.parse import quote


def normalize_phone(phone: str) -> str:
    return "".join(ch for ch in phone if ch.isdigit() or ch == "+")


def sms_link(phone: str, body: str, platform: str = "android") -> str:
    """iOS는 `sms:번호&body=`, 안드로이드는 `sms:번호?body=` 형식을 씁니다."""
    sep = "&" if platform == "ios" else "?"
    return f"sms:{normalize_phone(phone)}{sep}body={quote(body, safe='')}"
