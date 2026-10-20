import json
from pathlib import Path
from typing import Protocol

from models import Ride, RideStatus


class Repository(Protocol):
    def add(self, entity: Ride) -> None: ...
    def get(self, entity_id: int) -> Ride | None: ...
    def get_all(self) -> list[Ride]: ...
    def delete(self, entity_id: int) -> None: ...


class InMemoryRepository:
    def __init__(self) -> None:
        self._items: dict[int, Ride] = {}

    def add(self, entity: Ride) -> None:
        self._items[entity.id] = entity

    def get(self, entity_id: int) -> Ride | None:
        return self._items.get(entity_id)

    def get_all(self) -> list[Ride]:
        return list(self._items.values())

    def delete(self, entity_id: int) -> None:
        self._items.pop(entity_id, None)


class FileRepository:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self._items: dict[int, Ride] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        for item in json.loads(self.path.read_text(encoding="utf-8")):
            ride = Ride(item["id"], item["passenger"], item["distance_km"], item["car_type"], RideStatus(item["status"]), item["price"])
            self._items[ride.id] = ride

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = [{"id": r.id, "passenger": r.passenger, "distance_km": r.distance_km, "car_type": r.car_type, "status": r.status.value, "price": r.price} for r in self._items.values()]
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, entity: Ride) -> None:
        self._items[entity.id] = entity
        self._save()

    def get(self, entity_id: int) -> Ride | None:
        return self._items.get(entity_id)

    def get_all(self) -> list[Ride]:
        return list(self._items.values())

    def delete(self, entity_id: int) -> None:
        self._items.pop(entity_id, None)
        self._save()
