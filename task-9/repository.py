from typing import Protocol

from models import Car


class CarRepository(Protocol):
    def add(self, car: Car) -> Car: ...
    def get(self, car_id: int) -> Car | None: ...
    def get_all(self) -> list[Car]: ...
    def update(self, car: Car) -> Car: ...
    def delete(self, car_id: int) -> bool: ...


class InMemoryCarRepository:
    def __init__(self) -> None:
        self._cars: dict[int, Car] = {}
        self._next_id = 1

    def add(self, car: Car) -> Car:
        if car.id == 0:
            car.id = self._next_id
        self._next_id = max(self._next_id, car.id + 1)
        self._cars[car.id] = car
        return car

    def get(self, car_id: int) -> Car | None:
        return self._cars.get(car_id)

    def get_all(self) -> list[Car]:
        return list(self._cars.values())

    def update(self, car: Car) -> Car:
        if car.id not in self._cars:
            raise LookupError("Автомобиль не найден")
        self._cars[car.id] = car
        return car

    def delete(self, car_id: int) -> bool:
        return self._cars.pop(car_id, None) is not None
