# Лабораторная работа №10 — вариант 11, REST API такси

REST API реализован на Flask. Ресурс приложения — автомобиль такси `Car`.

## Запуск

Из папки `task-10`:

```text
python app.py
```

Сервер будет доступен по адресу `http://127.0.0.1:5000`.

Все запросы к `/cars` требуют заголовок:

```text
X-API-Key: taxi-demo-key
```

## Endpoint-ы

- `GET /cars` — список автомобилей, фильтры `category`, `available`, `min_id`, `max_id`, сортировка `sort` и `order`, пагинация `page` и `limit`.
- `GET /cars/<id>` — один автомобиль.
- `POST /cars` — создание.
- `PUT /cars/<id>` — полная замена.
- `PATCH /cars/<id>` — частичное изменение.
- `DELETE /cars/<id>` — удаление.
- `GET /cars/available` — специализированный endpoint свободных автомобилей.

Пример создания:

```text
POST /cars
X-API-Key: taxi-demo-key
Content-Type: application/json

{
  "make": "Toyota",
  "model": "Camry",
  "plate": "A111AA",
  "category": "comfort",
  "available": true
}
```

Дополнительно реализованы API key, middleware с логированием HTTP-метода, URL, статуса и времени, ETag для `/cars/available`, пагинация и отдельный HTTP-клиент на стандартной библиотеке.

## Проверка

```text
python test_api.py
```

Тесты проверяют полный CRUD-цикл, специализированный endpoint, ETag, фильтры, сортировку, пагинацию, API key, валидацию и ответ 404.
