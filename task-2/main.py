def read_text(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Значение не должно быть пустым.")


def read_number(prompt, minimum=0):
    while True:
        raw = input(prompt).strip().replace(",", ".")
        try:
            value = float(raw)
        except ValueError:
            print("Введите число.")
            continue
        if value < minimum:
            print(f"Значение должно быть не меньше {minimum}.")
            continue
        return value


def read_integer(prompt, minimum=1):
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Введите целое число.")
            continue
        if value < minimum:
            print(f"Значение должно быть не меньше {minimum}.")
            continue
        return value


def add_room(rooms):
    room = {
        "number": read_integer("Номер комнаты: "),
        "category": read_text("Категория: "),
        "price": read_number("Стоимость суток, руб.: "),
        "beds": read_integer("Количество мест: "),
        "status": read_text("Статус (свободен/занят): ").lower(),
    }
    rooms.append(room)
    print("Номер добавлен.")


def print_rooms(rooms):
    if not rooms:
        print("Список номеров пуст.")
        return
    for room in rooms:
        print(
            f"№{room['number']} | {room['category']} | "
            f"{room['price']:.2f} руб./сутки | мест: {room['beds']} | "
            f"{room['status']}"
        )


def find_available(rooms):
    return [room for room in rooms if room["status"] == "свободен"]


def find_by_category(rooms, category):
    return [room for room in rooms if room["category"].casefold() == category.casefold()]


def find_by_number(rooms, number):
    return [room for room in rooms if room["number"] == number]


def show_statistics(rooms):
    if not rooms:
        print("Нет данных для расчёта статистики.")
        return
    average_price = sum(room["price"] for room in rooms) / len(rooms)
    most_expensive = max(rooms, key=lambda room: room["price"])
    available_count = len(find_available(rooms))
    print(f"Средняя стоимость суток: {average_price:.2f} руб.")
    print(f"Самый дорогой номер: №{most_expensive['number']} ({most_expensive['price']:.2f} руб.)")
    print(f"Свободных номеров: {available_count} из {len(rooms)}")


def edit_room(rooms):
    number = read_integer("Номер комнаты для изменения: ")
    matches = find_by_number(rooms, number)
    if not matches:
        print("Номер не найден.")
        return
    room = matches[0]
    print("Оставьте поле пустым, чтобы сохранить текущее значение.")
    category = input(f"Категория [{room['category']}]: ").strip()
    if category:
        room["category"] = category
    price = input(f"Стоимость [{room['price']:.2f}]: ").strip().replace(",", ".")
    if price:
        try:
            new_price = float(price)
            if new_price < 0:
                raise ValueError
            room["price"] = new_price
        except ValueError:
            print("Некорректная стоимость, оставлено прежнее значение.")
    beds = input(f"Количество мест [{room['beds']}]: ").strip()
    if beds:
        try:
            new_beds = int(beds)
            if new_beds < 1:
                raise ValueError
            room["beds"] = new_beds
        except ValueError:
            print("Некорректное количество мест, оставлено прежнее значение.")
    status = input(f"Статус [{room['status']}]: ").strip()
    if status:
        room["status"] = status.lower()
    print("Данные номера обновлены.")


def main():
    rooms = []
    while True:
        print("\n===== Гостиничные номера =====")
        print("1. Добавить номер")
        print("2. Показать все номера")
        print("3. Найти свободные номера")
        print("4. Фильтр по категории")
        print("5. Сортировать по стоимости")
        print("6. Статистика")
        print("7. Уникальные категории")
        print("8. Изменить номер")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            add_room(rooms)
        elif choice == "2":
            print_rooms(rooms)
        elif choice == "3":
            available = find_available(rooms)
            print_rooms(available)
        elif choice == "4":
            category = read_text("Категория для поиска: ")
            print_rooms(find_by_category(rooms, category))
        elif choice == "5":
            print_rooms(sorted(rooms, key=lambda room: room["price"]))
        elif choice == "6":
            show_statistics(rooms)
        elif choice == "7":
            categories = {room["category"] for room in rooms}
            print("Категории:", ", ".join(sorted(categories)) if categories else "нет данных")
        elif choice == "8":
            edit_room(rooms)
        elif choice == "0":
            print("Работа завершена.")
            break
        else:
            print("Выберите пункт меню от 0 до 8.")


if __name__ == "__main__":
    main()
