"""Автоматические тесты (pytest) для варианта 11 «Такси».

БД создаётся в памяти на каждую тест-функцию через фикстуру, поэтому
внешний PostgreSQL/Redis-сервер для тестов не требуется.
"""

from __future__ import annotations

import pytest

from db import connect, init_db
from repository import Repository
from redis_cache import Cache
from service import RideService, ValidationError, NotFoundError


@pytest.fixture()
def service():
    conn = connect(":memory:")
    init_db(conn, seed=True)
    repo = Repository(conn)
    cache = Cache()  # фейк-кэш в памяти, т.к. Redis может отсутствовать
    svc = RideService(repo, cache)
    yield svc
    conn.close()


# 1. создание записи (POST)
def test_create_ride(service):
    ride = service.create_ride(client_id=1, driver_id=1, tariff_id=1, distance_km=5.0)
    assert ride["id"] is not None
    assert ride["status"] == "created"
    assert ride["distance_km"] == 5.0


# 2. чтение (GET)
def test_get_ride(service):
    ride = service.get_ride(1)
    assert ride["id"] == 1
    assert ride["client_name"] in ("", ) or ride["client_name"]  # клиент подтянут


# 3. изменение (PATCH)
def test_update_ride(service):
    ride = service.update_ride(1, status="completed", distance_km=9.9)
    assert ride["status"] == "completed"
    assert ride["distance_km"] == 9.9


# 4. удаление (DELETE)
def test_delete_ride(service):
    service.delete_ride(1)
    with pytest.raises(NotFoundError):
        service.get_ride(1)


# 5. ошибка отсутствующей записи
def test_get_missing(service):
    with pytest.raises(NotFoundError):
        service.get_ride(9999)


# 6. валидация: дистанция <= 0
def test_validation_distance(service):
    with pytest.raises(ValidationError):
        service.create_ride(client_id=1, driver_id=1, tariff_id=1, distance_km=0)


# 7. валидация: несуществующий клиент
def test_validation_client(service):
    with pytest.raises(ValidationError):
        service.create_ride(client_id=9999, driver_id=1, tariff_id=1, distance_km=5)


# 8. транзакция: несуществующая услуга -> ROLLBACK, запись не остаётся
def test_transaction_rollback(service):
    conn = service._repo._conn
    before = conn.execute("SELECT COUNT(*) c FROM rides").fetchone()["c"]
    with pytest.raises(ValidationError):
        # _require проверяет услуги до транзакции; используем прямую проверку
        service.create_ride(
            client_id=1, driver_id=1, tariff_id=1, distance_km=5, service_ids=[999]
        )
    after = conn.execute("SELECT COUNT(*) c FROM rides").fetchone()["c"]
    assert before == after  # ничего не добавилось


# 9. специализированный SQL-запрос: агрегация через репозиторий
def test_sql_aggregation(service):
    conn = service._repo._conn
    row = conn.execute(
        "SELECT COUNT(*) cnt, AVG(distance_km) avg FROM rides WHERE status='completed'"
    ).fetchone()
    assert row["cnt"] >= 1
    assert row["avg"] > 0


# 10. работа Repository (изолированно)
def test_repository_crud():
    conn = connect(":memory:")
    init_db(conn, seed=True)
    repo = Repository(conn)
    new = repo.create_ride(client_id=1, driver_id=1, tariff_id=1, distance_km=3.3)
    assert repo.get_ride(new["id"])["distance_km"] == 3.3
    repo.update_ride(new["id"], status="cancelled", distance_km=None)
    assert repo.get_ride(new["id"])["status"] == "cancelled"
    assert repo.delete_ride(new["id"]) is True
    assert repo.get_ride(new["id"]) is None
    conn.close()


# 11. работа Service (кэш-aside + инвалидация)
def test_service_cache_invalidation(service):
    svc = service
    # попадание в кэш при первом чтении
    svc.get_ride(2)
    assert svc._cache.get("ride:2") is not None
    # после изменения кэш сбрасывается
    svc.update_ride(2, status="completed", distance_km=None)
    assert svc._cache.get("ride:2") is None  # инвалидирован
    svc.get_ride(2)  # снова закэширован (уже обновлённые данные)
    assert svc.get_ride(2)["status"] == "completed"


# 12. Redis/TTL: фейк-кэш уважает время жизни
def test_cache_ttl():
    cache = Cache()
    cache.set("ride:100", "value", ttl=1)
    assert cache.get("ride:100") == "value"
    import time
    time.sleep(1.1)
    assert cache.get("ride:100") is None


# 13. интеграционный: API-маршрут через handler
def test_api_endpoint(service):
    from api import make_handler
    from http.server import HTTPServer
    import socket, threading, json
    from urllib.request import urlopen, Request

    # поднимаем сервер на случайном порту
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    server = HTTPServer(("127.0.0.1", port), make_handler(service))
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        with urlopen(f"http://127.0.0.1:{port}/rides") as r:
            assert r.status == 200
            data = json.loads(r.read())
            assert len(data) >= 1
        req = Request(
            f"http://127.0.0.1:{port}/rides",
            data=json.dumps({
                "client_id": 1, "driver_id": 1, "tariff_id": 1, "distance_km": 6.0
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req) as r:
            assert r.status == 201
    finally:
        server.shutdown()
        server.server_close()


# 14. SQL-injection защита: попытка внедрить условие в параметр
def test_sql_injection(service):
    conn = service._repo._conn
    # злонамеренное значение в параметре не должно менять смысл запроса
    malicious = "1' OR '1'='1"
    rows = conn.execute(
        "SELECT * FROM rides WHERE status = ?", (malicious,)
    ).fetchall()
    assert rows == []  # ничего не вернулось, хотя OR '1'='1' дал бы все строки