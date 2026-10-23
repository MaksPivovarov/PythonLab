from dataclasses import dataclass
from enum import Enum


class RideStatus(Enum):
    CREATED = "создан"
    ASSIGNED = "назначен"
    STARTED = "начат"
    COMPLETED = "завершён"


@dataclass
class Driver:
    id: int
    name: str


@dataclass
class Ride:
    id: int
    passenger: str
    distance_km: float
    status: RideStatus = RideStatus.CREATED
    driver: Driver | None = None
    price: float = 0.0
