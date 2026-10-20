from pathlib import Path

from models import Driver
from solid_app import (
    ConsoleNotifier,
    EconomyFare,
    InMemoryRideRepository,
    JsonRideRepository,
    PremiumFare,
    RideService,
    StandardFare,
)


def create_service() -> RideService:
    print("\nВыберите хранилище: 1. Память  2. JSON-файл")
    choice = input("Ваш выбор: ").strip()
    if choice == "2":
        repository = JsonRideRepository(str(Path(__file__).with_name("rides.json")))
    else:
        repository = InMemoryRideRepository()
    print("\nТариф: 1. Стандарт  2. Эконом  3. Премиум")
    fare_choice = input("Ваш выбор: ").strip()
    fare = {"1": StandardFare(), "2": EconomyFare(), "3": PremiumFare()}.get(fare_choice, StandardFare())
    return RideService(repository, ConsoleNotifier(), fare)


def main() -> None:
    service = create_service()
    drivers = [Driver(1, "Иван Петров"), Driver(2, "Анна Смирнова")]
    while True:
        print("\n===== Такси (SOLID) =====")
        print("1. Создать заказ")
        print("2. Показать заказы")
        print("3. Назначить водителя")
        print("4. Начать поездку")
        print("5. Завершить поездку")
        print("6. Средняя стоимость")
        print("0. Выход")
        choice = input("Действие: ").strip()
        try:
            if choice == "1":
                passenger = input("Пассажир: ")
                distance = float(input("Расстояние, км: ").replace(",", "."))
                ride = service.create_ride(passenger, distance)
                print(f"Стоимость: {ride.price:.2f} руб.")
            elif choice == "2":
                for ride in service.repository.get_all():
                    print(ride)
            elif choice == "3":
                ride_id = int(input("ID заказа: "))
                for driver in drivers:
                    print(f"{driver.id}. {driver.name}")
                driver_id = int(input("ID водителя: "))
                driver = next(item for item in drivers if item.id == driver_id)
                print(service.assign_driver(ride_id, driver))
            elif choice == "4":
                print(service.start(int(input("ID заказа: "))))
            elif choice == "5":
                print(service.finish(int(input("ID заказа: "))))
            elif choice == "6":
                print(f"Средняя стоимость: {service.average_price():.2f} руб.")
            elif choice == "0":
                break
            else:
                print("Неизвестная команда.")
        except (ValueError, LookupError, StopIteration) as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
