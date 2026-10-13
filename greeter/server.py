"""휴대폰 브라우저에서 여는 웹 화면 + JSON API (표준 라이브러리만 사용)."""
from __future__ import annotations

import json
from datetime import datetime
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .contacts import ContactBook
from .service import draft

INDEX = Path(__file__).parent / "static" / "index.html"


class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, book: ContactBook, use_ai: bool, **kwargs):
        self.book = book
        self.use_ai = use_ai
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, INDEX.read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/contacts":
            self.book.reload()
            today = datetime.now().date()
            self._json(200, [c.to_dict(today) for c in self.book.ordered(today)])
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(length) or b"{}")
            contact = self.book.get(body["id"])
        except (ValueError, KeyError):
            return self._json(400, {"error": "잘못된 요청입니다"})

        if self.path == "/api/draft":
            use_ai = self.use_ai and body.get("mode", "ai") == "ai"
            self._json(200, draft(contact, datetime.now(), use_ai, body.get("previous")))
        elif self.path == "/api/sent":
            today = datetime.now().date()
            self.book.mark_sent(contact.id, today)
            self._json(200, contact.to_dict(today))
        else:
            self._json(404, {"error": "not found"})

    def _json(self, status, data):
        self._send(status, json.dumps(data, ensure_ascii=False).encode(),
                   "application/json; charset=utf-8")

    def _send(self, status, payload: bytes, content_type: str):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)


def serve(book: ContactBook, host: str, port: int, use_ai: bool) -> None:
    httpd = ThreadingHTTPServer((host, port), partial(Handler, book=book, use_ai=use_ai))
    print(f"안부 문자 서비스: http://{host}:{port}  (종료: Ctrl+C)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
