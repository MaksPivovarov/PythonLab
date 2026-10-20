import os
from datetime import datetime

from exceptions import FlightNotFoundError, NoSeatsAvailableError
from models import Flight
from services import FlightService
from storage import JsonRepository

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_FILE = os.path.join(DATA_DIR, "flights.json")
CSV_FILE = os.path.join(DATA_DIR, "flights.csv")
LOG_FILE = os.path.join(DATA_DIR, "operations.log")


def write_log(message):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}\n")


def read_line(prompt, converter=str, minimum=None):
    while True:
        raw = input(prompt).strip()
        try:
            value = converter(raw)
            if minimum is not None and value < minimum:
                print(f"Значение должно быть не меньше {minimum}.")
                continue
            return value
        except ValueError:
            print("Введите корректное значение.")


def read_flight():
    number = read_line("Номер рейса: ").upper()
    destination = read_line("Направление: ")
    departure = read_line("Время отправления (ЧЧ:ММ): ")
    arrival = read_line("Время прибытия (ЧЧ:ММ): ")
    seats = read_line("Количество мест: ", int, 1)
    return Flight(number, destination, departure, arrival, seats)


def print_flights(flights):
    if not flights:
        print("Рейсы не найдены.")
        return
    for flight in flights:
        print(flight)


def build_service():
    repository = JsonRepository(DATA_FILE)
    return FlightService(repository, write_log)


def import_csv_into(service):
    path = input("Путь к CSV-файлу: ").strip()
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(__file__), path)
    if not os.path.exists(path):
        print("Файл не найден.")
        return
    try:
        imported = service.repository.import_csv(path)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Не удалось импортировать файл: {error}")
        return
    for flight in imported:
        if not any(item.number == flight.number for item in service.flights):
            service.flights.append(flight)
    service.save()
    print(f"Импортировано рейсов: {len(imported)}")


def main():
    service = build_service()
    print(f"Загружено рейсов: {len(service.flights)}")

    while True:
        print("\n===== Система учёта рейсов =====")
        print("1. Добавить рейс")
        print("2. Показать все рейсы")
        print("3. Найти по направлению")
        print("4. Забронировать место")
        print("5. Отменить бронирование")
        print("6. Экспорт в CSV")
        print("7. Импорт из CSV")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                flight = read_flight()
                service.add(flight)
                print("Рейс добавлен и сохранён.")
            elif choice == "2":
                print_flights(service.flights)
            elif choice == "3":
                destination = read_line("Направление для поиска: ")
                print_flights(service.find_by_destination(destination))
            elif choice == "4":
                service.book(read_line("Номер рейса: ").upper())
                print("Место забронировано.")
            elif choice == "5":
                service.cancel(read_line("Номер рейса: ").upper())
                print("Бронирование отменено.")
            elif choice == "6":
                service.export_csv(CSV_FILE)
                print(f"Данные сохранены в {CSV_FILE}")
            elif choice == "7":
                import_csv_into(service)
            elif choice == "0":
                print("Работа завершена.")
                break
            else:
                print("Неизвестный пункт меню.")
        except (FlightNotFoundError, NoSeatsAvailableError, ValueError) as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
