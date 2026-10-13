"""사용법:
  python -m greeter serve [--host 0.0.0.0] [--port 8000] [--no-ai]
  python -m greeter list                 # 연락할 때가 된 사람에게 보낼 초안 출력
  python -m greeter list --all --no-ai
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from .contacts import ContactBook
from .service import draft
from .sms import sms_link


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="greeter", description="가족·친구 안부 문자 도우미")
    p.add_argument("--contacts", type=Path, default=Path("contacts.json"))
    p.add_argument("--state", type=Path, default=Path("state.json"))
    p.add_argument("--no-ai", action="store_true", help="Claude API 없이 템플릿만 사용")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("serve", help="휴대폰에서 열 웹 화면 실행")
    s.add_argument("--host", default="127.0.0.1",
                   help="같은 Wi-Fi의 휴대폰에서 접속하려면 0.0.0.0")
    s.add_argument("--port", type=int, default=8000)

    ls = sub.add_parser("list", help="초안과 sms 링크를 터미널에 출력")
    ls.add_argument("--all", action="store_true", help="연락 주기가 안 된 사람도 포함")
    ls.add_argument("--ios", action="store_true", help="iPhone용 링크 형식")

    args = p.parse_args(argv)
    if not args.contacts.exists():
        print(f"{args.contacts} 파일이 없습니다. contacts.example.json을 복사해서 만드세요:\n"
              f"  cp contacts.example.json {args.contacts}", file=sys.stderr)
        return 1
    book = ContactBook(args.contacts, args.state)

    if args.cmd == "serve":
        from .server import serve
        serve(book, args.host, args.port, use_ai=not args.no_ai)
        return 0

    now = datetime.now()
    targets = [c for c in book.ordered(now.date()) if args.all or c.is_due(now.date())]
    if not targets:
        print("오늘은 연락할 때가 된 사람이 없어요. (--all 로 전체 보기)")
    warned = False
    for c in targets:
        d = draft(c, now, use_ai=not args.no_ai)
        if d.get("warning") and not warned:
            print(f"※ AI 대신 템플릿 사용: {d['warning']}\n", file=sys.stderr)
            warned = True
        print(f"■ {c.name} ({c.phone}) [{d['source']}]")
        print(f"  {d['text']}")
        print(f"  {sms_link(c.phone, d['text'], 'ios' if args.ios else 'android')}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
