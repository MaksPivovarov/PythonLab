class Transport:
    def __init__(self, name, route, speed):
        self.name = name
        self.route = route
        self._speed = 0
        self.speed = speed

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        if value <= 0:
            raise ValueError("Скорость должна быть больше нуля")
        self._speed = value

    def capacity(self):
        raise NotImplementedError

    def process(self):
        return f"{self.name}: вместимость {self.capacity()} пассажиров"

    def info(self):
        return f"{self.name} | маршрут: {self.route} | скорость: {self.speed} км/ч"


class Bus(Transport):
    def __init__(self, name, route, speed, seats):
        super().__init__(name, route, speed)
        self.seats = seats

    def capacity(self):
        return self.seats

    def process(self):
        return f"Автобус {self.name}: {self.capacity()} мест, маршрут {self.route}"


class Train(Transport):
    def __init__(self, name, route, speed, carriages, seats_per_carriage):
        super().__init__(name, route, speed)
        self.carriages = carriages
        self.seats_per_carriage = seats_per_carriage

    def capacity(self):
        return self.carriages * self.seats_per_carriage

    def process(self):
        return f"Поезд {self.name}: {self.carriages} вагонов, {self.capacity()} мест"


class Tram(Transport):
    def __init__(self, name, route, speed, sections, seats_per_section):
        super().__init__(name, route, speed)
        self.sections = sections
        self.seats_per_section = seats_per_section

    def capacity(self):
        return self.sections * self.seats_per_section

    def process(self):
        return f"Трамвай {self.name}: {self.sections} секции, {self.capacity()} мест"


class TransportSystem:
    def __init__(self, title):
        self.title = title
        self._transports = []

    def add(self, transport):
        self._transports.append(transport)

    def show_all(self):
        for transport in self._transports:
            print(transport.info())

    def show_capacity(self):
        for transport in self._transports:
            print(transport.process())

    def find(self, route=None, minimum_capacity=None):
        result = self._transports
        if route:
            result = [item for item in result if item.route.casefold() == route.casefold()]
        if minimum_capacity is not None:
            result = [item for item in result if item.capacity() >= minimum_capacity]
        return result

    def sorted_by_capacity(self):
        return sorted(self._transports, key=lambda item: item.capacity())

    def total_capacity(self):
        return sum(item.capacity() for item in self._transports)

    def average_speed(self):
        if not self._transports:
            return 0
        return sum(item.speed for item in self._transports) / len(self._transports)


def print_list(items):
    if not items:
        print("Подходящие объекты не найдены.")
        return
    for item in items:
        print(item.info(), f"| вместимость: {item.capacity()}")


def create_demo_system():
    system = TransportSystem("Городская транспортная система")
    system.add(Bus("Б-12", "Центр - Вокзал", 55, 42))
    system.add(Train("Э-1", "Центр - Вокзал", 90, 8, 78))
    system.add(Bus("Б-7", "Парк - Университет", 50, 35))
    system.add(Tram("Т-3", "Парк - Университет", 45, 2, 48))
    return system


def main():
    system = create_demo_system()
    print(system.title)
    while True:
        print("\n1. Показать транспорт")
        print("2. Показать вместимость")
        print("3. Найти по маршруту и вместимости")
        print("4. Сортировать по вместимости")
        print("5. Показать статистику")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            system.show_all()
        elif choice == "2":
            system.show_capacity()
        elif choice == "3":
            route = input("Маршрут (пусто — любой): ").strip()
            raw = input("Минимальная вместимость (пусто — без ограничения): ").strip()
            try:
                minimum = int(raw) if raw else None
                if minimum is not None and minimum < 0:
                    raise ValueError
                print_list(system.find(route or None, minimum))
            except ValueError:
                print("Вместимость должна быть неотрицательным целым числом.")
        elif choice == "4":
            print_list(system.sorted_by_capacity())
        elif choice == "5":
            print(f"Транспортных средств: {len(system._transports)}")
            print(f"Общая вместимость: {system.total_capacity()}")
            print(f"Средняя скорость: {system.average_speed():.1f} км/ч")
        elif choice == "0":
            print("Работа завершена.")
            break
        else:
            print("Неизвестный пункт меню.")


if __name__ == "__main__":
    main()
