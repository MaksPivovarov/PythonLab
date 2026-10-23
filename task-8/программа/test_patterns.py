from models import RideStatus
from observers_commands import CommandHistory, LogObserver, NotificationObserver, RideSubject, StatisticsObserver
from patterns import CarFactory, FareFactory
from repositories import InMemoryRepository
from service import TaxiService


def test_factory_and_strategy():
    assert CarFactory.create("бизнес") == "бизнес"
    assert FareFactory.create("ночной").calculate(10, "легковой") > FareFactory.create("стандарт").calculate(10, "легковой")


def setup():
    subject = RideSubject()
    subject.attach(LogObserver())
    subject.attach(NotificationObserver())
    subject.attach(StatisticsObserver())
    return TaxiService(InMemoryRepository(), FareFactory.create("стандарт"), subject, CommandHistory())


def test_create():
    service = setup()
    ride = service.create_ride("Иван", 10, "легковой")
    assert ride.price == 500
    assert len(service.repository.get_all()) == 1


def test_cancel():
    service = setup()
    ride = service.create_ride("Иван", 10, "легковой")
    service.cancel(ride.id)
    assert ride.status is RideStatus.CANCELLED


def test_recalculate():
    service = setup()
    ride = service.create_ride("Иван", 10, "легковой")
    old = ride.price
    service.recalculate(ride.id, "ночной")
    assert ride.price > old
    assert ride.status is RideStatus.CALCULATED


def test_undo():
    service = setup()
    service.create_ride("Иван", 10, "легковой")
    service.history.undo()
    assert service.repository.get_all() == []


def test_empty_average():
    assert setup().average_price() == 0


if __name__ == "__main__":
    tests = [value for name, value in globals().items() if name.startswith("test_")]
    for test in tests:
        test()
    print(f"Пройдено тестов: {len(tests)}")
