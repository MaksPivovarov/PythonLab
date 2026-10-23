"""REST API поверх http.server (без внешних зависимостей).

Маршруты:
  GET    /rides          — список поездок
  GET    /rides/{id}     — поездка + услуги (включает Redis cache-aside)
  POST   /rides          — создать поездку (транзакция)
  PATCH  /rides/{id}     — изменить статус/дистанцию (транзакция)
  DELETE /rides/{id}     — удалить поездку (транзакция)

Слой соединения вручную близок к стандартной библиотеке, чтобы
не требовать установки FastAPI/flask для основной части.
"""

from __future__ import annotations

import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from service import RideService, ValidationError, NotFoundError

_RIDE_RE = re.compile(r"^/rides/(\d+)$")


class RestHandler(BaseHTTPRequestHandler):
    service: RideService  # инжектим извне

    # ------- вспомогательные -------
    def _send(self, status: int, payload) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length == 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError:
            raise ValidationError("Некорректный JSON")

    # ------- маршрутизация -------
    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/rides":
            self._send(200, self.service.list_rides())
            return
        m = _RIDE_RE.match(path)
        if m:
            try:
                ride = self.service.get_ride_full(int(m.group(1)))
                self._send(200, ride)
            except NotFoundError as e:
                self._send(404, {"error": str(e)})
            return
        self._send(404, {"error": "Не найдено"})

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/rides":
            self._send(404, {"error": "Не найдено"})
            return
        try:
            data = self._read_json()
            ride = self.service.create_ride(
                client_id=data.get("client_id"),
                driver_id=data.get("driver_id"),
                tariff_id=data.get("tariff_id"),
                distance_km=float(data.get("distance_km", 0)),
                service_ids=data.get("service_ids") or None,
            )
            self._send(201, ride)
        except (ValidationError, ValueError, TypeError) as e:
            self._send(400, {"error": str(e)})

    def do_PATCH(self) -> None:  # noqa: N802
        m = _RIDE_RE.match(urlparse(self.path).path)
        if not m:
            self._send(404, {"error": "Не найдено"})
            return
        try:
            data = self._read_json()
            ride = self.service.update_ride(
                ride_id=int(m.group(1)),
                status=data.get("status"),
                distance_km=data.get("distance_km"),
            )
            self._send(200, ride)
        except NotFoundError as e:
            self._send(404, {"error": str(e)})
        except (ValidationError, ValueError, TypeError) as e:
            self._send(400, {"error": str(e)})

    def do_DELETE(self) -> None:  # noqa: N802
        m = _RIDE_RE.match(urlparse(self.path).path)
        if not m:
            self._send(404, {"error": "Не найдено"})
            return
        try:
            self.service.delete_ride(int(m.group(1)))
            self._send(200, {"deleted": int(m.group(1))})
        except NotFoundError as e:
            self._send(404, {"error": str(e)})

    def log_message(self, fmt: str, *args) -> None:  # noqa: N802
        print(f"[API] {self.client_address[0]} - {fmt % args}")


def make_handler(service: RideService):
    """Возвращает класс-обработчик с внедрённым сервисом."""
    cls = RestHandler
    cls.service = service
    return cls


def run_api(service: RideService, port: int = 8000, bind: str = "127.0.0.1") -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((bind, port), make_handler(service))
    print(f"REST API on http://{bind}:{port}")
    return server