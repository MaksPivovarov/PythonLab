from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class RideStatus(Enum):
    CREATED = "создана"
    ASSIGNED = "назначена"
    IN_PROGRESS = "выполняется"
    COMPLETED = "завершена"
    CANCELLED = "отменена"

    def __str__(self) -> str:
        return self.value


@dataclass
class Car:
    model: str
    plate: str


@dataclass
class Driver:
    name: str
    car: Car


@dataclass
class Ride:
    id: int
    passenger: str
    driver: Optional[Driver]
    distance_km: float
    rate_per_km: float
    status: RideStatus = RideStatus.CREATED

    def price(self) -> float:
        return self.distance_km * self.rate_per_km

    def set_status(self, status: RideStatus) -> None:
        self.status = status

    def __str__(self) -> str:
        driver = self.driver.name if self.driver else "не назначен"
        return (f"Поездка #{self.id} | {self.passenger} -> {driver} | "
                f"{self.distance_km} км x {self.rate_per_km} руб. = "
                f"{self.price():.2f} руб. | {self.status}")


@dataclass
class RideRegistry:
    rides: list[Ride] = field(default_factory=list)

    def add(self, ride: Ride) -> None:
        self.rides.append(ride)

    def find(self, ride_id: int) -> Optional[Ride]:
        for ride in self.rides:
            if ride.id == ride_id:
                return ride
        return None

    def remove(self, ride_id: int) -> None:
        ride = self.find(ride_id)
        if ride is None:
            raise LookupError(f"Поездка #{ride_id} не найдена")
        self.rides.remove(ride)
