from dataclasses import dataclass
from enum import Enum


class RideStatus(Enum):
    CREATED = "создана"
    CALCULATED = "рассчитана"
    CANCELLED = "отменена"


@dataclass
class Ride:
    id: int
    passenger: str
    distance_km: float
    car_type: str
    status: RideStatus = RideStatus.CREATED
    price: float = 0.0

    def __str__(self) -> str:
        return f"#{self.id} {self.passenger}: {self.distance_km} км, {self.car_type}, {self.price:.2f} руб., {self.status.value}"
