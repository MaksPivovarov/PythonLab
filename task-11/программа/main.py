"""Точка входа: собирает все слои приложения и запускает API + CDN.

Запуск:  python main.py [--seed]
Установка Redis не обязательна — при её отсутствии используется
фейк-кэш в памяти (см. redis_cache.py).
"""

from __future__ import annotations

import argparse
import threading

from api import run_api
from cdn import run_cdn
from db import connect, init_db
from redis_cache import Cache
from repository import Repository
from service import RideService

DB_PATH = "taxi.db"


def build(db_path: str = DB_PATH, seed: bool = False) -> tuple[RideService, Cache]:
    conn = connect(db_path)
    init_db(conn, seed=seed)
    cache = Cache()
    repo = Repository(conn)
    service = RideService(repo, cache)
    return service, cache


def main() -> None:
    parser = argparse.ArgumentParser(description="Такси: REST + SQL + Redis + CDN")
    parser.add_argument("--seed", action="store_true", help="наполнить БД тестовыми данными")
    parser.add_argument("--api-port", type=int, default=8000)
    parser.add_argument("--cdn-port", type=int, default=8090)
    parser.add_argument("--no-cdn", action="store_true", help="не запускать CDN")
    args = parser.parse_args()

    service, _cache = build(seed=args.seed)

    api_server = run_api(service, port=args.api_port)
    threading.Thread(target=api_server.serve_forever, daemon=True).start()

    if not args.no_cdn:
        cdn_server = run_cdn(port=args.cdn_port)
        cdn_thread = threading.Thread(target=cdn_server.serve_forever, daemon=True)
        cdn_thread.start()

    print("Готово. Нажмите Ctrl+C для остановки.")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\nОстановка...")


if __name__ == "__main__":
    main()