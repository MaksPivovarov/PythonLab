"""Сервисный слой: бизнес-логика, транзакции, cache-aside.

Здесь сосредоточена логика, которая использует Repository (SQL)
и Cache (Redis). Разделение: Repository — «как достать данные»,
Service — «какая бизнес-правило применяется».
"""

from __future__ import annotations

import json
from typing import Any

from redis_cache import Cache
from repository import Repository

TTL_DEFAULT = 60  # секунды жизни кэша


class ValidationError(Exception):
    """Ошибка валидации входных данных."""


class NotFoundError(Exception):
    """Сущность не найдена."""


def _cache_key(ride_id: int) -> str:
    return f"ride:{ride_id}"


class RideService:
    def __init__(self, repo: Repository, cache: Cache) -> None:
        self._repo = repo
        self._cache = cache

    # ---------- READ: cache-aside ----------
    def list_rides(self) -> list[dict[str, Any]]:
        return self._repo.get_all_rides()

    def get_ride(self, ride_id: int) -> dict[str, Any]:
        cache_key = _cache_key(ride_id)
        # 1) пробуем кэш
        cached = self._cache.get(cache_key)
        if cached is not None:
            return json.loads(cached)
        # 2) кэш пуст -> БД
        ride = self._repo.get_ride(ride_id)
        if ride is None:
            raise NotFoundError(f"Поездка {ride_id} не найдена")
        # 3) наполняем кэш с TTL
        self._cache.set(cache_key, json.dumps(ride, ensure_ascii=False), TTL_DEFAULT)
        return ride

    def get_ride_full(self, ride_id: int) -> dict[str, Any]:
        ride = self.get_ride(ride_id)
        ride["services"] = self._repo.get_ride_services(ride_id)
        return ride

    # ---------- CREATE: транзакция ----------
    def create_ride(
        self,
        client_id: int,
        driver_id: int,
        tariff_id: int,
        distance_km: float,
        service_ids: list[int] | None = None,
    ) -> dict[str, Any]:
        if distance_km <= 0:
            raise ValidationError("distance_km должен быть > 0")
        self._require(client_id, driver_id, tariff_id, service_ids)

        conn = self._repo._conn  # доступ для управления транзакцией
        conn.execute("BEGIN")
        try:
            ride = self._repo.create_ride(
                client_id, driver_id, tariff_id, distance_km, service_ids
            )
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        # после записи кэш нельзя доверять
        self._cache.delete(_cache_key(ride["id"]))
        return ride

    # ---------- UPDATE: транзакция + сброс кэша ----------
    def update_ride(
        self, ride_id: int, status: str | None, distance_km: float | None
    ) -> dict[str, Any]:
        if ride_id <= 0:
            raise ValidationError("Некорректный ride_id")
        if status is not None and status not in (
            "created", "in_progress", "completed", "cancelled",
        ):
            raise ValidationError(f"Недопустимый статус: {status}")
        if distance_km is not None and distance_km <= 0:
            raise ValidationError("distance_km должен быть > 0")

        existing = self._repo.get_ride(ride_id)
        if existing is None:
            raise NotFoundError(f"Поездка {ride_id} не найдена")

        conn = self._repo._conn
        conn.execute("BEGIN")
        try:
            ride = self._repo.update_ride(ride_id, status, distance_km)
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        # cache invalidation
        self._cache.delete(_cache_key(ride_id))
        return ride

    # ---------- DELETE: транзакция + сброс кэша ----------
    def delete_ride(self, ride_id: int) -> None:
        existing = self._repo.get_ride(ride_id)
        if existing is None:
            raise NotFoundError(f"Поездка {ride_id} не найдена")
        conn = self._repo._conn
        conn.execute("BEGIN")
        try:
            self._repo.delete_ride(ride_id)
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        self._cache.delete(_cache_key(ride_id))

    # ---------- вспомогательное ----------
    def _require(
        self, client_id: int, driver_id: int, tariff_id: int, service_ids: list[int] | None
    ) -> None:
        if not self._repo.client_exists(client_id):
            raise ValidationError(f"Клиент {client_id} не существует")
        if not self._repo.driver_exists(driver_id):
            raise ValidationError(f"Водитель {driver_id} не существует")
        if not self._repo.tariff_exists(tariff_id):
            raise ValidationError(f"Тариф {tariff_id} не существует")
        for sid in (service_ids or []):
            if not self._repo.service_exists(sid):
                raise ValidationError(f"Услуга {sid} не существует")