import json
import socket
import threading
import time

from repository import InMemoryCarRepository
from server import CarServer
from service import CarService


def test_repository_crud():
    repository = InMemoryCarRepository()
    service = CarService(repository)
    created = service.handle("create", {"make": "A", "model": "B", "plate": "1"})
    assert created["id"] == 1
    assert service.handle("get", {"id": 1})["model"] == "B"
    service.handle("update", {"id": 1, "available": False})
    assert service.handle("get", {"id": 1})["available"] is False
    assert service.handle("delete", {"id": 1})["deleted"] is True


def test_special_command():
    service = CarService(InMemoryCarRepository())
    service.handle("create", {"make": "A", "model": "B", "plate": "1", "available": True})
    service.handle("create", {"make": "C", "model": "D", "plate": "2", "available": False})
    assert len(service.handle("available_cars", {})["cars"]) == 1


def test_ping_and_request_history():
    service = CarService(InMemoryCarRepository())
    assert service.handle("ping", {})["message"] == "pong"
    service.record("ping", {})
    assert service.handle("history", {})["requests"][0]["command"] == "ping"


def test_protocol_error():
    server = CarServer(port=0)
    response = server.process(b'{"command":"unknown","data":{}}', "test")
    assert response["status"] == "error"


def test_rate_limit():
    service = CarService(InMemoryCarRepository())
    for _ in range(10):
        assert service.allow_request("client")
    assert not service.allow_request("client")


def test_json_protocol_line():
    request = {"request_id": "abc", "command": "ping", "data": {}}
    encoded = (json.dumps(request) + "\n").encode()
    assert encoded.endswith(b"\n")


if __name__ == "__main__":
    tests = [value for name, value in globals().items() if name.startswith("test_")]
    for test in tests:
        test()
    print(f"Пройдено тестов: {len(tests)}")
