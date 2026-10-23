"""Репозиторий доступа к реляционной БД.

Выполняет только SQL через параметризованные запросы (защита от
SQL-injection). Никакой бизнес-логики — только работа с данными.
"""

from __future__ import annotations

import sqlite3
from typing import Any


class RepositoryError(Exception):
    """Ошибка уровня работы с БД."""


class Repository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    # ---------- чтение ----------
    def get_all_rides(self) -> list[dict[str, Any]]:
        cur = self._conn.execute(
            """
            SELECT r.id, r.created_at, r.status, r.distance_km,
                   c.full_name AS client_name,
                   d.full_name AS driver_name,
                   d.car_brand || ' ' || d.car_plate AS car,
                   t.name AS tariff,
                   round(t.base_price + t.price_per_km * r.distance_km, 2) AS cost
            FROM rides r
            JOIN clients c   ON c.id = r.client_id
            JOIN drivers d   ON d.id = r.driver_id
            JOIN tariffs t   ON t.id = r.tariff_id
            ORDER BY r.id
            """
        )
        return [dict(row) for row in cur.fetchall()]

    def get_ride(self, ride_id: int) -> dict[str, Any] | None:
        cur = self._conn.execute(
            """
            SELECT r.id, r.created_at, r.status, r.distance_km,
                   r.client_id, r.driver_id, r.tariff_id,
                   c.full_name AS client_name,
                   d.full_name AS driver_name,
                   t.name AS tariff,
                   round(t.base_price + t.price_per_km * r.distance_km, 2) AS cost
            FROM rides r
            JOIN clients c ON c.id = r.client_id
            JOIN drivers d ON d.id = r.driver_id
            JOIN tariffs t ON t.id = r.tariff_id
            WHERE r.id = ?
            """,
            (ride_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def get_ride_services(self, ride_id: int) -> list[dict[str, Any]]:
        cur = self._conn.execute(
            """
            SELECT s.name, s.price, rs.quantity
            FROM ride_services rs
            JOIN services s ON s.id = rs.service_id
            WHERE rs.ride_id = ?
            """,
            (ride_id,),
        )
        return [dict(row) for row in cur.fetchall()]

    # ---------- запись ----------
    def create_ride(
        self,
        client_id: int,
        driver_id: int,
        tariff_id: int,
        distance_km: float,
        service_ids: list[int] | None = None,
    ) -> dict[str, Any] | None:
        """Создаёт поездку (и при необходимости связи N:M).

        Вся операция выполняется внутри одной транзакции начатой в
        Service: если что-то падает, вызывается ROLLBACK.
        """
        cur = self._conn.execute(
            """
            INSERT INTO rides (client_id, driver_id, tariff_id, distance_km, status)
            VALUES (?, ?, ?, ?, 'created')
            """,
            (client_id, driver_id, tariff_id, distance_km),
        )
        ride_id = cur.lastrowid

        for sid in (service_ids or []):
            self._conn.execute(
                "INSERT INTO ride_services (ride_id, service_id) VALUES (?, ?)",
                (ride_id, sid),
            )
        return self.get_ride(ride_id)

    def update_ride(
        self, ride_id: int, status: str | None, distance_km: float | None
    ) -> dict[str, Any] | None:
        fields: list[str] = []
        params: list[Any] = []
        if status is not None:
            fields.append("status = ?")
            params.append(status)
        if distance_km is not None:
            fields.append("distance_km = ?")
            params.append(distance_km)
        if not fields:
            return self.get_ride(ride_id)
        params.append(ride_id)
        self._conn.execute(
            f"UPDATE rides SET {', '.join(fields)} WHERE id = ?", params
        )
        return self.get_ride(ride_id)

    def delete_ride(self, ride_id: int) -> bool:
        """Удаляет поездку вместе со связями N:M (каскад вручную)."""
        self._conn.execute("DELETE FROM ride_services WHERE ride_id = ?", (ride_id,))
        cur = self._conn.execute("DELETE FROM reviews WHERE ride_id = ?", (ride_id,))
        cur2 = self._conn.execute("DELETE FROM rides WHERE id = ?", (ride_id,))
        return cur2.rowcount > 0

    # ---------- вспомогательные проверки ----------
    def client_exists(self, client_id: int) -> bool:
        cur = self._conn.execute("SELECT 1 FROM clients WHERE id = ?", (client_id,))
        return cur.fetchone() is not None

    def driver_exists(self, driver_id: int) -> bool:
        cur = self._conn.execute("SELECT 1 FROM drivers WHERE id = ?", (driver_id,))
        return cur.fetchone() is not None

    def tariff_exists(self, tariff_id: int) -> bool:
        cur = self._conn.execute("SELECT 1 FROM tariffs WHERE id = ?", (tariff_id,))
        return cur.fetchone() is not None

    def service_exists(self, service_id: int) -> bool:
        cur = self._conn.execute("SELECT 1 FROM services WHERE id = ?", (service_id,))
        return cur.fetchone() is not None