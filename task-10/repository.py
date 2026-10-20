from models import Car


class CarRepository:
    def __init__(self) -> None:
        self._cars: dict[int, Car] = {}
        self._next_id = 1

    def get_all(self) -> list[Car]:
        return list(self._cars.values())

    def get_by_id(self, car_id: int) -> Car | None:
        return self._cars.get(car_id)

    def create(self, car: Car) -> Car:
        car.id = self._next_id
        self._next_id += 1
        self._cars[car.id] = car
        return car

    def update(self, car: Car) -> Car:
        self._cars[car.id] = car
        return car

    def delete(self, car_id: int) -> bool:
        return self._cars.pop(car_id, None) is not None
