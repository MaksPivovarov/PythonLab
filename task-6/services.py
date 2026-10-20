import inspect
from dataclasses import dataclass
from typing import Any

from decorators import command, log_call, measure_time, require_status
from models import Car, Driver, Ride, RideRegistry, RideStatus


class RideService:
    def __init__(self, registry: RideRegistry | None = None) -> None:
        self.registry = registry or RideRegistry()
        self.drivers = [
            Driver("Иван Петров", Car("Kia Rio", "А123АА")),
            Driver("Анна Смирнова", Car("Hyundai Solaris", "В456ВВ")),
        ]

    @command("Добавить поездку")
    @log_call
    def add_ride(self, passenger: str, distance: float, rate: float) -> Ride:
        if not passenger.strip() or distance <= 0 or rate < 0:
            raise ValueError("Проверьте имя пассажира, расстояние и тариф")
        ride = Ride(len(self.registry.rides) + 1, passenger.strip(), None, distance, rate)
        self.registry.add(ride)
        return ride

    @command("Назначить водителя")
    @log_call
    def assign_driver(self, ride_id: int, driver_index: int) -> Ride:
        ride = self._get_ride(ride_id)
        if not 1 <= driver_index <= len(self.drivers):
            raise ValueError("Нет водителя с таким номером")
        if ride.status != RideStatus.CREATED:
            raise ValueError("Водителя можно назначить только созданной поездке")
        ride.driver = self.drivers[driver_index - 1]
        ride.set_status(RideStatus.ASSIGNED)
        return ride

    @command("Изменить статус")
    @log_call
    def start_ride(self, ride_id: int) -> Ride:
        ride = self._get_ride(ride_id)
        if ride.status != RideStatus.ASSIGNED:
            raise ValueError("Начать можно только назначенную поездку")
        ride.set_status(RideStatus.IN_PROGRESS)
        return ride

    @command("Завершить поездку")
    @require_status(RideStatus.IN_PROGRESS)
    @log_call
    def complete_ride(self, ride_id: int) -> Ride:
        ride = self._get_ride(ride_id)
        ride.set_status(RideStatus.COMPLETED)
        return ride

    @command("Отменить поездку")
    @require_status(RideStatus.CREATED, RideStatus.ASSIGNED)
    @log_call
    def cancel_ride(self, ride_id: int) -> Ride:
        ride = self._get_ride(ride_id)
        ride.set_status(RideStatus.CANCELLED)
        return ride

    @command("Удалить поездку")
    def delete_ride(self, ride_id: int) -> None:
        self.registry.remove(ride_id)

    def _get_ride(self, ride_id: int) -> Ride:
        ride = self.registry.find(ride_id)
        if ride is None:
            raise LookupError(f"Поездка #{ride_id} не найдена")
        return ride

    @measure_time
    def statistics(self) -> dict[str, Any]:
        rides = self.registry.rides
        prices = [ride.price() for ride in rides]
        completed = sum(ride.status == RideStatus.COMPLETED for ride in rides)
        return {
            "count": len(rides),
            "completed": completed,
            "average_price": sum(prices) / len(prices) if prices else 0,
            "minimum_price": min(prices, default=0),
            "maximum_price": max(prices, default=0),
        }

    def registered_commands(self) -> list[tuple[str, str]]:
        commands = []
        for name, method in inspect.getmembers(self, predicate=callable):
            title = getattr(method, "command_title", None)
            if title:
                commands.append((name, title))
        return commands

    def execute_command(self, name: str, *args: Any) -> Any:
        method = getattr(self, name, None)
        if method is None or not callable(method) or not hasattr(getattr(type(self), name, None), "command_title"):
            raise ValueError("Команда не найдена")
        return method(*args)


@dataclass
class TaxiCompany:
    name: str
    service: RideService

    def report(self) -> str:
        stats = self.service.statistics()
        return f"{self.name}: поездок {stats['count']}, средняя стоимость {stats['average_price']:.2f} руб."
