import json
import logging
import socket
import threading
from typing import Any

from repository import InMemoryCarRepository
from service import CarService

HOST = "127.0.0.1"
PORT = 5050


class CarServer:
    def __init__(self, host: str = HOST, port: int = PORT) -> None:
        self.host = host
        self.port = port
        self.service = CarService(InMemoryCarRepository())
        self.running = True
        self.server_socket: socket.socket | None = None

    def seed(self) -> None:
        for data in (
            {"make": "Toyota", "model": "Camry", "plate": "A111AA", "available": True},
            {"make": "Kia", "model": "Rio", "plate": "B222BB", "available": False},
            {"make": "Hyundai", "model": "Solaris", "plate": "C333CC", "available": True},
        ):
            self.service.handle("create", data)

    def start(self) -> None:
        logging.info("Сервер запущен на %s:%s", self.host, self.port)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            self.server_socket = server
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.port))
            server.listen()
            server.settimeout(1.0)
            while self.running:
                try:
                    connection, address = server.accept()
                except socket.timeout:
                    continue
                except OSError:
                    if not self.running:
                        break
                    raise
                threading.Thread(target=self.handle_client, args=(connection, address), daemon=True).start()

    def handle_client(self, connection: socket.socket, address: Any) -> None:
        with connection:
            connection.settimeout(5.0)
            buffer = b""
            while self.running:
                try:
                    chunk = connection.recv(4096)
                except socket.timeout:
                    return
                if not chunk:
                    return
                buffer += chunk
                while b"\n" in buffer:
                    raw, buffer = buffer.split(b"\n", 1)
                    if not raw:
                        continue
                    response = self.process(raw, str(address))
                    connection.sendall((json.dumps(response, ensure_ascii=False) + "\n").encode("utf-8"))

    def process(self, raw: bytes, client: str) -> dict:
        request_id = None
        try:
            request = json.loads(raw.decode("utf-8"))
            request_id = request.get("request_id")
            command = request["command"]
            data = request.get("data", {})
            if not self.service.allow_request(client):
                raise RuntimeError("Слишком много запросов")
            result = self.service.handle(command, data)
            self.service.record(command, data)
            return {"status": "ok", "data": result, "request_id": request_id}
        except (ValueError, KeyError, TypeError, LookupError, RuntimeError, json.JSONDecodeError) as error:
            logging.warning("Ошибка запроса: %s", error)
            return {"status": "error", "error": str(error), "request_id": request_id}

    def stop(self) -> None:
        self.running = False
        if self.server_socket:
            self.server_socket.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    server = CarServer()
    server.seed()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
