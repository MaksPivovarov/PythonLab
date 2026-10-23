from exceptions import CarNotFoundError, ValidationError
from models import Car


class CarService:
    ALLOWED_FIELDS = {"make", "model", "plate", "category", "available", "driver"}

    def __init__(self, repository) -> None:
        self.repository = repository

    def list_cars(self, category=None, available=None, min_id=None, max_id=None, sort="id", order="asc") -> list[Car]:
        cars = self.repository.get_all()
        if category:
            cars = [car for car in cars if car.category.casefold() == category.casefold()]
        if available is not None:
            cars = [car for car in cars if car.available is available]
        if min_id is not None:
            cars = [car for car in cars if car.id >= min_id]
        if max_id is not None:
            cars = [car for car in cars if car.id <= max_id]
        if sort not in {"id", "make", "category", "plate"}:
            raise ValidationError("Недопустимое поле сортировки")
        if order not in {"asc", "desc"}:
            raise ValidationError("order должен быть asc или desc")
        return sorted(cars, key=lambda car: getattr(car, sort), reverse=order == "desc")

    def get(self, car_id: int) -> Car:
        car = self.repository.get_by_id(car_id)
        if car is None:
            raise CarNotFoundError(f"Автомобиль {car_id} не найден")
        return car

    def create(self, data: dict) -> Car:
        required = ("make", "model", "plate", "category")
        if any(not str(data.get(field, "")).strip() for field in required):
            raise ValidationError("Поля make, model, plate и category обязательны")
        return self.repository.create(Car(0, *(str(data[key]).strip() for key in required), bool(data.get("available", True)), str(data.get("driver", ""))))

    def replace(self, car_id: int, data: dict) -> Car:
        self.get(car_id)
        required = ("make", "model", "plate", "category")
        if any(not str(data.get(field, "")).strip() for field in required):
            raise ValidationError("PUT требует make, model, plate и category")
        car = Car(car_id, *(str(data[key]).strip() for key in required), bool(data.get("available", True)), str(data.get("driver", "")))
        return self.repository.update(car)

    def patch(self, car_id: int, data: dict) -> Car:
        car = self.get(car_id)
        if not data or set(data) - self.ALLOWED_FIELDS:
            raise ValidationError("Пустое тело или неизвестные поля")
        for field, value in data.items():
            setattr(car, field, value)
        return self.repository.update(car)

    def delete(self, car_id: int) -> None:
        self.get(car_id)
        self.repository.delete(car_id)

    def available_cars(self) -> list[Car]:
        return [car for car in self.repository.get_all() if car.available]
