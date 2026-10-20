import os
import tempfile

from models import Driver, RideStatus
from solid_app import (
    ConsoleNotifier,
    EconomyFare,
    InMemoryRideRepository,
    JsonRideRepository,
    PremiumFare,
    RideService,
    StandardFare,
)


def make_service(fare=None, repository=None):
    return RideService(repository or InMemoryRideRepository(), ConsoleNotifier(), fare or StandardFare())


def test_create_ride():
    service = make_service()
    ride = service.create_ride("Олег", 10)
    assert ride.id == 1
    assert ride.price == 550


def test_assign_start_finish():
    service = make_service()
    ride = service.create_ride("Олег", 10)
    service.assign_driver(ride.id, Driver(1, "Иван"))
    service.start(ride.id)
    service.finish(ride.id)
    assert ride.status is RideStatus.COMPLETED


def test_invalid_transition():
    service = make_service()
    ride = service.create_ride("Олег", 10)
    try:
        service.finish(ride.id)
    except ValueError:
        pass
    else:
        raise AssertionError("Ожидалась ошибка перехода")


def test_fare_strategies():
    assert EconomyFare().calculate(10) < StandardFare().calculate(10) < PremiumFare().calculate(10)


def test_average_price():
    service = make_service()
    service.create_ride("Олег", 10)
    service.create_ride("Анна", 20)
    assert service.average_price() == 775


def test_json_repository():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "rides.json")
        service = make_service(repository=JsonRideRepository(path))
        service.create_ride("Олег", 10)
        loaded = JsonRideRepository(path)
        assert len(loaded.get_all()) == 1


if __name__ == "__main__":
    tests = [value for name, value in globals().items() if name.startswith("test_")]
    for test in tests:
        test()
    print(f"Пройдено тестов: {len(tests)}")
