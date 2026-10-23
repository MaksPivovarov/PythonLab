"""Подключение к реляционной базе данных (sqlite3)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "schema.sql"
SEED_PATH = Path(__file__).parent / "seed.sql"


def connect(db_path: str | Path) -> sqlite3.Connection:
    """Открывает соединение с включёнными FK и row_factory."""
    # check_same_thread=False: HTTP-сервер обрабатывает запросы в потоках,
    # а соединение создаётся в основном. Для учебного приложения этого
    # достаточно (нет конкурентной записи из нескольких потоков).
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection, seed: bool = False) -> None:
    """Создаёт таблицы и, при необходимости, наполняет тестовыми данными."""
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    if seed:
        # seed выполняется таким образом, что при повторном запуске
        # (когда в БД уже есть данные) не падает: для учебного скрипта
        # достаточно выполнить только при пустой таблице rides.
        cur = conn.execute("SELECT COUNT(*) FROM rides")
        if cur.fetchone()[0] == 0:
            conn.executescript(SEED_PATH.read_text(encoding="utf-8"))
    conn.commit()