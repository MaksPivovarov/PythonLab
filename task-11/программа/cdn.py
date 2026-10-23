"""Имитация CDN: раздаёт статические ресурсы локально.

В настоящем проекте вместо этого используется внешний CDN
(Cloudflare / R2 + CDN). Здесь даётся локальная имитация отдельного
сервера статического контента с поддержкой Cache-Control, чтобы
исследовать заголовки и поведение кэша.
"""

from __future__ import annotations

import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# Разным типам ресурсов — разное время кэширования.
CACHE_MAX_AGE: dict[str, int] = {
    ".css": 3600,
    ".js": 3600,
    ".jpg": 86400,
    ".png": 86400,
}

forwarded = 0


def _cache_control(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    maxage = CACHE_MAX_AGE.get(ext, 60)
    return f"public, max-age={maxage}"


class CdnHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        global forwarded
        rel = self.path.lstrip("/")
        if "?" in rel:
            rel = rel.split("?", 1)[0]
        full = os.path.normpath(os.path.join(STATIC_DIR, rel))
        # защита от выхода за пределы static/
        if not full.startswith(os.path.normpath(STATIC_DIR)) or not os.path.isfile(full):
            self.send_error(404, "Not Found")
            return

        ctype, _ = mimetypes.guess_type(full)
        with open(full, "rb") as f:
            body = f.read()

        forwarded += 1
        self.send_response(200)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", _cache_control(full))
        self.send_header("X-CDN-Node", "edge-msk-01")
        self.send_header("X-CDN-File", os.path.basename(full))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:  # noqa: N802
        print(f"[CDN] {self.client_address[0]} - {fmt % args}")


def run_cdn(port: int = 8090, bind: str = "127.0.0.1") -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((bind, port), CdnHandler)
    print(f"CDN (local imitation / origin server) on http://{bind}:{port}")
    return server