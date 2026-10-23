from pathlib import Path

from observers_commands import CommandHistory, LogObserver, NotificationObserver, RideSubject, StatisticsObserver
from patterns import FareFactory
from repositories import FileRepository, InMemoryRepository
from service import TaxiService


def create_app():
    print("Хранилище: 1. Память  2. JSON-файл")
    choice = input("Выберите: ").strip()
    repository = FileRepository(str(Path(__file__).with_name("rides.json"))) if choice == "2" else InMemoryRepository()
    print("Тариф: стандарт, ночной, повышенный")
    tariff = input("Выберите тариф: ").strip().lower() or "стандарт"
    tariff = {"1": "стандарт", "2": "ночной", "3": "повышенный"}.get(tariff, tariff)
    strategy = FareFactory.create(tariff)
    subject = RideSubject()
    logger = LogObserver()
    notification = NotificationObserver()
    statistics = StatisticsObserver()
    for observer in (logger, notification, statistics):
        subject.attach(observer)
    return TaxiService(repository, strategy, subject, CommandHistory()), statistics


def main():
    service, statistics = create_app()
    while True:
        print("\n=== Такси ===")
        print("1. Создать заказ")
        print("2. Показать заказы")
        print("3. Отменить заказ")
        print("4. Пересчитать тариф")
        print("5. Средняя стоимость")
        print("6. История событий")
        print("7. Undo последней команды")
        print("0. Выход")
        choice = input("Действие: ").strip()
        try:
            if choice == "1":
                passenger = input("Пассажир: ").strip()
                distance = float(input("Расстояние, км: ").replace(",", "."))
                car = input("Автомобиль (легковой/комфорт/бизнес): ").strip().lower()
                print(service.create_ride(passenger, distance, car))
            elif choice == "2":
                rides = service.repository.get_all()
                if not rides:
                    print("Заказов нет.")
                for ride in rides:
                    print(ride)
            elif choice == "3":
                print(service.cancel(int(input("ID заказа: "))))
            elif choice == "4":
                ride_id = int(input("ID заказа: "))
                tariff = input("Тариф (стандарт/ночной/повышенный): ").strip().lower()
                print(service.recalculate(ride_id, tariff))
            elif choice == "5":
                print(f"Средняя стоимость: {service.average_price():.2f} руб.")
            elif choice == "6":
                print("События:", logger.events)
                print("Счётчики:", dict(statistics.events))
            elif choice == "7":
                service.history.undo()
                print("Последняя команда отменена.")
            elif choice == "0":
                break
            else:
                print("Неизвестная команда.")
        except (ValueError, LookupError) as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
