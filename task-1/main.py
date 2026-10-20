MONTHS = (
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
)


def read_positive_number(prompt):
    while True:
        value = input(prompt).strip().replace(",", ".")
        try:
            number = float(value)
        except ValueError:
            print("Введите число.")
            continue
        if number <= 0:
            print("Значение должно быть больше нуля.")
            continue
        return number


def read_integer(prompt, minimum=1):
    while True:
        value = input(prompt).strip()
        try:
            number = int(value)
        except ValueError:
            print("Введите целое число.")
            continue
        if number < minimum:
            print(f"Число должно быть не меньше {minimum}.")
            continue
        return number


def read_consumption():
    values = []
    print("Введите потребление по месяцам в кВт·ч.")
    for month in MONTHS:
        values.append(read_positive_number(f"{month}: "))
    return values


def calculate_statistics(values, tariff):
    total = sum(values)
    average = total / len(values)
    maximum = max(values)
    max_month = MONTHS[values.index(maximum)]
    above_average = sum(value > average for value in values)
    minimum = min(values)
    min_month = MONTHS[values.index(minimum)]
    cost = total * tariff
    return total, average, max_month, maximum, above_average, min_month, minimum, cost


def print_statistics(values, tariff, number):
    total, average, max_month, maximum, above_average, min_month, minimum, cost = calculate_statistics(values, tariff)
    print(f"\nНабор данных {number}")
    print(f"Годовое потребление: {total:.2f} кВт·ч")
    print(f"Среднемесячное потребление: {average:.2f} кВт·ч")
    print(f"Максимальное потребление: {max_month} ({maximum:.2f} кВт·ч)")
    print(f"Минимальное потребление: {min_month} ({minimum:.2f} кВт·ч)")
    print(f"Месяцев выше среднего: {above_average}")
    print(f"Примерная стоимость: {cost:.2f} руб.")


def main():
    datasets = []
    tariff = read_positive_number("Введите тариф за 1 кВт·ч, руб.: ")

    while True:
        print("\n===== Анализ электроэнергии =====")
        print("1. Ввести набор данных")
        print("2. Показать статистику")
        print("3. Изменить тариф")
        print("4. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            datasets.append(read_consumption())
            print("Набор данных сохранён.")
        elif choice == "2":
            if not datasets:
                print("Сначала введите хотя бы один набор данных.")
            else:
                for number, values in enumerate(datasets, 1):
                    print_statistics(values, tariff, number)
        elif choice == "3":
            tariff = read_positive_number("Новый тариф, руб./кВт·ч: ")
        elif choice == "4":
            print("Работа завершена.")
            break
        else:
            print("Выберите пункт меню от 1 до 4.")


if __name__ == "__main__":
    main()
