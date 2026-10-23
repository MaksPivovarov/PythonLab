import logging
import time
from collections import deque

from models import Car


class CarService:
    def __init__(self, repository) -> None:
        self.repository = repository
        self.history: deque[dict] = deque(maxlen=50)
        self.requests: dict[str, deque[float]] = {}

    def handle(self, command: str, data: dict) -> dict:
        if command == "list":
            return {"cars": [car.to_dict() for car in self.repository.get_all()]}
        if command == "get":
            car = self.repository.get(int(data["id"]))
            if car is None:
                raise LookupError("Автомобиль не найден")
            return car.to_dict()
        if command == "create":
            car = Car(0, data["make"], data["model"], data["plate"], bool(data.get("available", True)))
            return self.repository.add(car).to_dict()
        if command == "update":
            car = self.repository.get(int(data["id"]))
            if car is None:
                raise LookupError("Автомобиль не найден")
            for field in ("make", "model", "plate", "available"):
                if field in data:
                    setattr(car, field, data[field])
            return self.repository.update(car).to_dict()
        if command == "delete":
            if not self.repository.delete(int(data["id"])):
                raise LookupError("Автомобиль не найден")
            return {"deleted": True}
        if command == "available_cars":
            return {"cars": [car.to_dict() for car in self.repository.get_all() if car.available]}
        if command == "ping":
            return {"message": "pong", "timestamp": time.time()}
        if command == "history":
            return {"requests": list(self.history)}
        raise ValueError(f"Неизвестная команда: {command}")

    def record(self, command: str, data: dict) -> None:
        self.history.append({"command": command, "data": data})

    def allow_request(self, client: str, limit: int = 10, period: float = 10.0) -> bool:
        now = time.monotonic()
        timestamps = self.requests.setdefault(client, deque())
        while timestamps and now - timestamps[0] > period:
            timestamps.popleft()
        if len(timestamps) >= limit:
            return False
        timestamps.append(now)
        return True
