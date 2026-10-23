from generators import FlightIterator, flights_to_destination, flights_with_seats
from models import CharterFlight, Flight, InternationalFlight
from operations import (
    all_positive_prices,
    average_price,
    cheapest,
    filter_objects,
    has_destination,
    process_pipeline,
    sort_objects,
    transform_objects,
)


def create_flights():
    return [
        Flight("SU101", "Москва - Сочи", 12500, 24, "вылет"),
        InternationalFlight("SU205", "Москва - Стамбул", 31800, 12, "вылет", "Турция"),
        CharterFlight("FV310", "Санкт-Петербург - Сочи", 9800, 0, "задержан", "Север"),
        Flight("S7120", "Москва - Казань", 7600, 8, "вылет"),
        InternationalFlight("U6230", "Москва - Минск", 15400, 17, "вылет", "Беларусь"),
        CharterFlight("N412", "Казань - Сочи", 11200, 5, "вылет", "Восток"),
    ]


def print_flights(flights):
    found = False
    for flight in flights:
        print(flight)
        found = True
    if not found:
        print("Рейсы не найдены.")


def show_pipeline(flights):
    result = process_pipeline(
        flights,
        lambda flight: flight.price <= 20000,
        lambda flight: flight,
        lambda flight: flight.free_seats,
        lambda flight: flight.free_seats > 0,
    )
    print_flights(result)


def main():
    flights = create_flights()
    while True:
        print("\n===== Обработка авиарейсов =====")
        print("1. Показать рейсы")
        print("2. Фильтр по максимальной цене")
        print("3. Показать номера рейсов")
        print("4. Сортировать по свободным местам")
        print("5. Показать самый дешёвый рейс")
        print("6. Проверить направление")
        print("7. Генератор рейсов со свободными местами")
        print("8. Конвейер обработки")
        print("9. Показать список и генератор значений")
        print("10. Собственный итератор")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                print_flights(flights)
            elif choice == "2":
                maximum = float(input("Максимальная стоимость: ").replace(",", "."))
                print_flights(filter_objects(flights, lambda flight: flight.price <= maximum))
            elif choice == "3":
                numbers = list(transform_objects(flights, lambda flight: flight.number))
                print(", ".join(numbers))
            elif choice == "4":
                print_flights(sort_objects(flights, lambda flight: flight.free_seats))
            elif choice == "5":
                print(cheapest(flights))
            elif choice == "6":
                destination = input("Направление: ").strip()
                print("Рейсы найдены." if has_destination(flights, destination) else "Рейсов в этом направлении нет.")
                print_flights(flights_to_destination(flights, destination))
            elif choice == "7":
                print_flights(flights_with_seats(flights))
            elif choice == "8":
                show_pipeline(flights)
            elif choice == "9":
                list_values = [flight.price for flight in flights]
                lazy_values = (flight.price for flight in flights)
                print(f"Список хранит {len(list_values)} значений сразу.")
                print("Генератор вычисляет по запросу; первые цены:", next(lazy_values), next(lazy_values))
            elif choice == "10":
                iterator = FlightIterator(flights)
                print(next(iterator))
                print(next(iterator))
                print("Оставшиеся объекты:")
                print_flights(iterator)
            elif choice == "0":
                print("Работа завершена.")
                break
            else:
                print("Неизвестный пункт меню.")
        except (ValueError, StopIteration) as error:
            print(f"Некорректная операция или ввод: {error}")

    print(f"Средняя стоимость: {average_price(flights):.2f} руб.")
    print("Все цены допустимы:", all_positive_prices(flights))


if __name__ == "__main__":
    main()
