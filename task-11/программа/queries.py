"""Набор из 15+ учебных SQL-запросов для варианта 11 (Такси).

Каждый запрос продемонстрирован через параметризованный вызов.
Для выполнения: python queries.py
"""

from __future__ import annotations

from db import connect, init_db
from pathlib import Path

DB = Path(__file__).parent / "taxi.db"


def run_all() -> None:
    conn = connect(DB)
    init_db(conn, seed=True)
    q = conn.execute

    print("=" * 70)

    # 1. SELECT -- выбрать всё
    print("\n1. SELECT * FROM rides")
    for row in q("SELECT * FROM rides LIMIT 3"): print(dict(row))

    # 2. WHERE -- фильтрация
    print("\n2. WHERE status = 'completed'")
    for row in q("SELECT id, status FROM rides WHERE status = 'completed'"): print(dict(row))

    # 3. ORDER BY -- сортировка
    print("\n3. ORDER BY distance_km DESC")
    for row in q("SELECT id, distance_km FROM rides ORDER BY distance_km DESC LIMIT 3"): print(dict(row))

    # 4. JOIN -- связь двух таблиц
    print("\n4. JOIN: rides -> drivers")
    for row in q(
        "SELECT r.id, d.full_name FROM rides r JOIN drivers d ON d.id = r.driver_id LIMIT 3"
    ): print(dict(row))

    # 5. LEFT JOIN -- поездки и их отзывы (включая поездки без отзыва)
    print("\n5. LEFT JOIN: rides -> reviews (появятся и поездки без отзывов, cnt=0)")
    for row in q(
        """SELECT r.id, COUNT(review.id) AS reviews
           FROM rides r LEFT JOIN reviews review ON review.ride_id = r.id
           GROUP BY r.id"""
    ): print(dict(row))

    # 6. GROUP BY + 8. COUNT -- количество поедок по статусу
    print("\n6, 8. GROUP BY status, COUNT(*)")
    for row in q("SELECT status, COUNT(*) AS cnt FROM rides GROUP BY status"): print(dict(row))

    # 7. HAVING -- статусы с числом поездок >= 2
    print("\n7. HAVING COUNT(*) >= 2")
    for row in q("SELECT status, COUNT(*) c FROM rides GROUP BY status HAVING COUNT(*) >= 2"): print(dict(row))

    # 9. SUM/AVG
    print("\n9. AVG(price_per_km), SUM")  # от тарифов
    for row in q("SELECT AVG(price_per_km) avg_price FROM tariffs"): print(dict(row))

    # 10. INSERT
    print("\n10. INSERT в reviews")
    cur = conn.execute(
        "INSERT INTO reviews (ride_id, rating, comment) VALUES (?, ?, ?)", (1, 5, 'тест')
    )
    print("inserted id:", cur.lastrowid)
    conn.rollback()  # откатываем тестовую вставку

    # 11. UPDATE
    print("\n11. UPDATE -- изменить статус поездки 9")
    cur = conn.execute("UPDATE rides SET status = 'in_progress' WHERE id = 9")
    print("rows updated:", cur.rowcount)
    conn.rollback()

    # 12. DELETE
    print("\n12. DELETE -- удалить несуществующий id (0 строк)")
    cur = conn.execute("DELETE FROM rides WHERE id = 99999")
    print("rows deleted:", cur.rowcount)

    # 13. подзапрос
    print("\n13. Подзапрос -- поездки дальше средней дистанции")
    for row in q(
        """SELECT id, distance_km FROM rides
           WHERE distance_km > (SELECT AVG(distance_km) FROM rides)"""
    ): print(dict(row))

    # 14. несколько условий
    print("\n14. Несколько условий: completed и distance > 5")
    for row in q(
        "SELECT id FROM rides WHERE status = 'completed' AND distance_km > 5"
    ): print(dict(row))

    # 15. связь нескольких таблиц (3+ JOIN)
    print("\n15. JOIN 3 таблиц: ride + client + driver")
    for row in q(
        """SELECT r.id, c.full_name AS client, d.full_name AS driver
           FROM rides r
           JOIN clients c ON c.id = r.client_id
           JOIN drivers d ON d.id = r.driver_id LIMIT 3"""
    ): print(dict(row))

    # N:M через промежуточную таблицу (дополнительно)
    print("\nДоп. N:M -- поездки и услуги")
    for row in q(
        """SELECT r.id, s.name FROM rides r
           JOIN ride_services rs ON rs.ride_id = r.id
           JOIN services s ON s.id = rs.service_id LIMIT 5"""
    ): print(dict(row))

    # стоимость поездки (формула)
    print("\nДоп. -- расчёт стоимости поездки")
    for row in q(
        """SELECT r.id, t.name, t.base_price + t.price_per_km * r.distance_km AS cost
           FROM rides r JOIN tariffs t ON t.id = r.tariff_id LIMIT 3"""
    ): print(dict(row))

    conn.close()


if __name__ == "__main__":
    run_all()