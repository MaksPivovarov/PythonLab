import inspect
from pathlib import Path

from context import OperationLogger
from models import Ride, RideRegistry, RideStatus
from protocols import print_report
from services import RideService, TaxiCompany

LOG_PATH = Path(__file__).with_name("operations.log")


def show_rides(service: RideService) -> None:
    if not service.registry.rides:
        print("Поездок нет.")
        return
    for ride in service.registry.rides:
        print(ride)


def inspect_ride(ride: Ride) -> None:
    print("=== ИНТРОСПЕКЦИЯ ===")
    print("type:", type(ride).__name__)
    print("isinstance Ride:", isinstance(ride, Ride))
    print("isinstance status Enum:", isinstance(ride.status, RideStatus))
    print("class MRO:", ride.__class__.__mro__)
    print("hasattr price:", hasattr(ride, "price"))
    print("price:", getattr(ride, "price")())
    print("dataclass fields:", list(ride.__dataclass_fields__))
    print("methods:", [name for name, member in inspect.getmembers(ride, callable) if not name.startswith("_")])
    print("price signature:", inspect.signature(ride.price))


def seed(service: RideService) -> None:
    service.add_ride("Алексей", 12.5, 55)
    service.add_ride("Мария", 8, 60)
    service.assign_driver(1, 1)
    service.start_ride(1)


def main() -> None:
    service = RideService()
    seed(service)
    company = TaxiCompany("Городское такси", service)

    while True:
        print("\n===== Система такси =====")
        print("1. Показать поездки")
        print("2. Добавить поездку")
        print("3. Назначить водителя")
        print("4. Начать поездку")
        print("5. Завершить поездку")
        print("6. Отменить поездку")
        print("7. Статистика")
        print("8. Интроспекция")
        print("9. Декораторы и контекстный менеджер")
        print("10. Автоматические команды")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                show_rides(service)
            elif choice == "2":
                passenger = input("Пассажир: ").strip()
                distance = float(input("Расстояние, км: ").replace(",", "."))
                rate = float(input("Тариф за км: ").replace(",", "."))
                print(service.add_ride(passenger, distance, rate))
            elif choice == "3":
                ride_id = int(input("ID поездки: "))
                print("1. Иван Петров, Kia Rio")
                print("2. Анна Смирнова, Hyundai Solaris")
                print(service.assign_driver(ride_id, int(input("Номер водителя: "))))
            elif choice == "4":
                print(service.start_ride(int(input("ID поездки: "))))
            elif choice == "5":
                print(service.complete_ride(int(input("ID поездки: "))))
            elif choice == "6":
                print(service.cancel_ride(int(input("ID поездки: "))))
            elif choice == "7":
                print(service.statistics())
            elif choice == "8":
                if service.registry.rides:
                    inspect_ride(service.registry.rides[0])
            elif choice == "9":
                with OperationLogger("calculate_statistics", {"rides": len(service.registry.rides)}, LOG_PATH):
                    print(service.statistics())
                print_report(company)
            elif choice == "10":
                for name, title in service.registered_commands():
                    print(f"{name}: {title}")
            elif choice == "0":
                print("Работа завершена.")
                break
            else:
                print("Неизвестный пункт меню.")
        except (ValueError, LookupError) as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
