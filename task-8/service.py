from copy import deepcopy

from models import Ride, RideStatus
from observers_commands import CommandHistory, CreateRideCommand, RideSubject
from patterns import CarFactory, FareFactory


class TaxiService:
    def __init__(self, repository, strategy, subject: RideSubject, history: CommandHistory) -> None:
        self.repository = repository
        self.strategy = strategy
        self.subject = subject
        self.history = history

    def create_ride(self, passenger: str, distance_km: float, car_type: str) -> Ride:
        if not passenger.strip() or distance_km <= 0:
            raise ValueError("Некорректные данные заказа")
        car_type = CarFactory.create(car_type)
        ride = Ride(self._next_id(), passenger, distance_km, car_type)
        ride.price = self.strategy.calculate(distance_km, car_type)
        ride.price *= CarFactory.multiplier(car_type)
        self.history.execute(CreateRideCommand(self, ride))
        return ride

    def cancel(self, ride_id: int) -> Ride:
        ride = self._get(ride_id)
        ride.status = RideStatus.CANCELLED
        self.repository.add(ride)
        self.subject.notify("отмена заказа", ride)
        return ride

    def recalculate(self, ride_id: int, tariff: str) -> Ride:
        ride = self._get(ride_id)
        self.strategy = FareFactory.create(tariff)
        ride.price = self.strategy.calculate(ride.distance_km, ride.car_type) * CarFactory.multiplier(ride.car_type)
        ride.status = RideStatus.CALCULATED
        self.repository.add(ride)
        self.subject.notify("перерасчёт стоимости", ride)
        return ride

    def average_price(self) -> float:
        rides = self.repository.get_all()
        return sum(ride.price for ride in rides) / len(rides) if rides else 0.0

    def _next_id(self) -> int:
        return max((ride.id for ride in self.repository.get_all()), default=0) + 1

    def _get(self, ride_id: int) -> Ride:
        ride = self.repository.get(ride_id)
        if ride is None:
            raise LookupError(f"Заказ #{ride_id} не найден")
        return ride
