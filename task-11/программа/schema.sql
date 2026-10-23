-- ============================================================
-- Вариант 11: Такси
-- Реляционная схема: 5 таблиц, связи 1:N и N:M
-- ============================================================

-- Водители
CREATE TABLE IF NOT EXISTS drivers (
    id          INTEGER PRIMARY KEY,
    full_name   TEXT    NOT NULL,
    phone       TEXT    NOT NULL UNIQUE,
    car_brand   TEXT    NOT NULL,
    car_plate   TEXT    NOT NULL UNIQUE
);

-- Клиенты (таблица клиентов используется и как "users")
CREATE TABLE IF NOT EXISTS clients (
    id         INTEGER PRIMARY KEY,
    full_name  TEXT    NOT NULL,
    phone      TEXT    NOT NULL UNIQUE,
    rating     REAL    NOT NULL DEFAULT 5.0 CHECK (rating >= 0 AND rating <= 5)
);

-- Тарифы
CREATE TABLE IF NOT EXISTS tariffs (
    id           INTEGER PRIMARY KEY,
    name         TEXT    NOT NULL UNIQUE,
    price_per_km REAL    NOT NULL CHECK (price_per_km > 0),
    base_price   REAL    NOT NULL CHECK (base_price >= 0)
);

-- Поездки (Ride) — основная сущность. 1:N с клиентами, водителями, тарифами.
CREATE TABLE IF NOT EXISTS rides (
    id          INTEGER PRIMARY KEY,
    client_id   INTEGER NOT NULL,
    driver_id   INTEGER NOT NULL,
    tariff_id   INTEGER NOT NULL,
    distance_km REAL    NOT NULL CHECK (distance_km > 0),
    status      TEXT    NOT NULL DEFAULT 'created'
                CHECK (status IN ('created', 'in_progress', 'completed', 'cancelled')),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    FOREIGN KEY (tariff_id) REFERENCES tariffs(id)
);

-- Отзывы о поездке (1:N с rides), нормализация: отзыв вынесен отдельно от ride.
CREATE TABLE IF NOT EXISTS reviews (
    id            INTEGER PRIMARY KEY,
    ride_id       INTEGER NOT NULL,
    rating        INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment       TEXT,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (ride_id) REFERENCES rides(id)
);

-- Дополнительные услуги (например, детское кресло). N:M через промежуточную таблицу.
CREATE TABLE IF NOT EXISTS services (
    id            INTEGER PRIMARY KEY,
    name          TEXT    NOT NULL UNIQUE,
    price         REAL    NOT NULL CHECK (price >= 0)
);

-- Промежуточная таблица для связи N:M rides <-> services
CREATE TABLE IF NOT EXISTS ride_services (
    ride_id     INTEGER NOT NULL,
    service_id  INTEGER NOT NULL,
    quantity    INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    PRIMARY KEY (ride_id, service_id),
    FOREIGN KEY (ride_id)    REFERENCES rides(id),
    FOREIGN KEY (service_id) REFERENCES services(id)
);

-- ============================================================
-- Индексы
-- ============================================================
-- 1) Дорогой запрос по умолчанию: поиск активных поездок по статусу.
CREATE INDEX IF NOT EXISTS idx_rides_status ON rides(status);

-- 2) JOIN rides -> clients; фильтр поездок клиента.
CREATE INDEX IF NOT EXISTS idx_rides_client ON rides(client_id);

-- 3) JOIN rides -> reviews.
CREATE INDEX IF NOT EXISTS idx_reviews_ride ON reviews(ride_id);