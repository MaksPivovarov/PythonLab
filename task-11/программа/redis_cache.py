"""Кэш через Redis с безопасным fallback.

Если redis-py не установлен или сервер Redis недоступен, кэш превращается
в no-op фейк, и приложение продолжает работать (читает только из Postgres/
SQLite). Это позволяет запускать лабораторную без Redis-сервера.
"""

from __future__ import annotations

import time
from typing import Any, Optional, Tuple

try:
    import redis as redis_lib  # type: ignore

    _HAS_REDIS = True
except Exception:  # pragma: no cover
    redis_lib = None  # type: ignore
    _HAS_REDIS = False


class Cache:
    """Единый интерфейс кэша: реальный Redis или фейк в памяти."""

    def __init__(self, url: str = "redis://localhost:6379/0") -> None:
        self._fake: dict[str, tuple[Optional[str], float]] = {}
        if _HAS_REDIS:
            try:
                self._client = redis_lib.Redis.from_url(url, decode_responses=True)
                self._client.ping()
                self._real = True
            except Exception:
                self._real = False
                self._client = None
        else:
            self._real = False
            self._client = None
        if not self._real:
            print("[cache] Redis недоступен — использую фейк-кэш в памяти")

    @property
    def is_real(self) -> bool:
        return self._real

    def get(self, key: str) -> Optional[str]:
        if self._real:
            return self._client.get(key)  # type: ignore
        entry = self._fake.get(key)
        if not entry:
            return None
        val, expires = entry
        if expires is not None and time.time() > expires:
            self._fake.pop(key, None)
            return None
        return val

    def set(self, key: str, value: Any, ttl: int) -> None:
        text = str(value)
        if self._real:
            self._client.set(key, text, ex=ttl)  # type: ignore
            return
        self._fake[key] = (text, time.time() + ttl)

    def delete(self, key: str) -> bool:
        if self._real:
            return bool(self._client.delete(key))  # type: ignore
        return self._fake.pop(key, None) is not None

    def incr(self, key: str, ttl: int = 3600) -> int:
        if self._real:
            n = self._client.incr(key)  # type: ignore
            self._client.expire(key, ttl)  # type: ignore
            return n
        entry = self._fake.get(key)
        n = int(entry[0]) + 1 if entry and entry[0] else 1
        self._fake[key] = (str(n), time.time() + ttl)
        return n  # type: ignore

    def expire(self, key: str, ttl: int) -> bool:
        if self._real:
            return bool(self._client.expire(key, ttl))  # type: ignore
        entry = self._fake.get(key)
        if entry:
            self._fake[key] = (entry[0], time.time() + ttl)
        return entry is not None

    def flush(self) -> None:
        if self._real:
            self._client.flushdb()  # type: ignore
        self._fake.clear()