from abc import ABC, abstractmethod
from typing import Callable

from models import Ride


class FareStrategy(ABC):
    @abstractmethod
    def calculate(self, distance_km: float, car_type: str) -> float:
        ...


class StandardFare(FareStrategy):
    def calculate(self, distance_km: float, car_type: str) -> float:
        return 100 + distance_km * 40


class NightFare(FareStrategy):
    def calculate(self, distance_km: float, car_type: str) -> float:
        return 130 + distance_km * 52


class SurgeFare(FareStrategy):
    def calculate(self, distance_km: float, car_type: str) -> float:
        return (100 + distance_km * 40) * 1.5


class FareFactory:
    _strategies: dict[str, Callable[[], FareStrategy]] = {
        "стандарт": StandardFare,
        "ночной": NightFare,
        "повышенный": SurgeFare,
    }

    @classmethod
    def create(cls, name: str) -> FareStrategy:
        key = {"1": "стандарт", "2": "ночной", "3": "повышенный", "standard": "стандарт", "night": "ночной", "surge": "повышенный"}.get(name.casefold(), name.casefold())
        try:
            return cls._strategies[key]()
        except KeyError as error:
            raise ValueError("Неизвестный тариф") from error


class CarFactory:
    _rates = {"легковой": 1.0, "комфорт": 1.3, "бизнес": 1.8}

    @classmethod
    def create(cls, car_type: str) -> str:
        key = {"1": "легковой", "2": "комфорт", "3": "бизнес", "economy": "легковой", "comfort": "комфорт", "business": "бизнес"}.get(car_type.casefold(), car_type.casefold())
        if key not in cls._rates:
            raise ValueError("Неизвестный тип автомобиля")
        return key

    @classmethod
    def multiplier(cls, car_type: str) -> float:
        return cls._rates[car_type]
