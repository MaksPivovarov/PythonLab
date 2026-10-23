from abc import ABC, abstractmethod
import json
from pathlib import Path
from typing import Protocol

from models import Driver, Ride, RideStatus


class RideRepository(Protocol):
    def add(self, ride: Ride) -> None: ...
    def get(self, ride_id: int) -> Ride | None: ...
    def get_all(self) -> list[Ride]: ...
    def update(self, ride: Ride) -> None: ...


class Notifier(Protocol):
    def notify(self, message: str) -> None: ...


class FareStrategy(ABC):
    @abstractmethod
    def calculate(self, distance_km: float) -> float:
        ...


class StandardFare(FareStrategy):
    def calculate(self, distance_km: float) -> float:
        return 100 + distance_km * 45


class EconomyFare(FareStrategy):
    def calculate(self, distance_km: float) -> float:
        return 70 + distance_km * 32


class PremiumFare(FareStrategy):
    def calculate(self, distance_km: float) -> float:
        return 180 + distance_km * 75


class InMemoryRideRepository:
    def __init__(self) -> None:
        self._rides: dict[int, Ride] = {}

    def add(self, ride: Ride) -> None:
        self._rides[ride.id] = ride

    def get(self, ride_id: int) -> Ride | None:
        return self._rides.get(ride_id)

    def get_all(self) -> list[Ride]:
        return list(self._rides.values())

    def update(self, ride: Ride) -> None:
        self._rides[ride.id] = ride


class JsonRideRepository:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self._rides: dict[int, Ride] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        for item in data:
            driver = Driver(**item["driver"]) if item.get("driver") else None
            ride = Ride(item["id"], item["passenger"], item["distance_km"], RideStatus(item["status"]), driver, item["price"])
            self._rides[ride.id] = ride

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = []
        for ride in self._rides.values():
            data.append({
                "id": ride.id, "passenger": ride.passenger,
                "distance_km": ride.distance_km, "status": ride.status.value,
                "driver": vars(ride.driver) if ride.driver else None,
                "price": ride.price,
            })
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, ride: Ride) -> None:
        self._rides[ride.id] = ride
        self._save()

    def get(self, ride_id: int) -> Ride | None:
        return self._rides.get(ride_id)

    def get_all(self) -> list[Ride]:
        return list(self._rides.values())

    def update(self, ride: Ride) -> None:
        self._rides[ride.id] = ride
        self._save()


class ConsoleNotifier:
    def notify(self, message: str) -> None:
        print(message)


class RideService:
    def __init__(self, repository: RideRepository, notifier: Notifier, fare: FareStrategy) -> None:
        self.repository = repository
        self.notifier = notifier
        self.fare = fare

    def create_ride(self, passenger: str, distance_km: float) -> Ride:
        if not passenger.strip() or distance_km <= 0:
            raise ValueError("Некорректные данные поездки")
        ids = [ride.id for ride in self.repository.get_all()]
        ride = Ride(max(ids, default=0) + 1, passenger, distance_km, price=self.fare.calculate(distance_km))
        self.repository.add(ride)
        self.notifier.notify(f"Создан заказ #{ride.id}")
        return ride

    def assign_driver(self, ride_id: int, driver: Driver) -> Ride:
        ride = self._get(ride_id)
        if ride.status is not RideStatus.CREATED:
            raise ValueError("Водителя можно назначить только созданному заказу")
        ride.driver = driver
        ride.status = RideStatus.ASSIGNED
        self.repository.update(ride)
        return ride

    def start(self, ride_id: int) -> Ride:
        ride = self._get(ride_id)
        if ride.status is not RideStatus.ASSIGNED:
            raise ValueError("Поездка не назначена водителю")
        ride.status = RideStatus.STARTED
        self.repository.update(ride)
        return ride

    def finish(self, ride_id: int) -> Ride:
        ride = self._get(ride_id)
        if ride.status is not RideStatus.STARTED:
            raise ValueError("Поездка ещё не начата")
        ride.status = RideStatus.COMPLETED
        self.repository.update(ride)
        return ride

    def average_price(self) -> float:
        rides = self.repository.get_all()
        return sum(ride.price for ride in rides) / len(rides) if rides else 0.0

    def _get(self, ride_id: int) -> Ride:
        ride = self.repository.get(ride_id)
        if ride is None:
            raise LookupError(f"Заказ #{ride_id} не найден")
        return ride
