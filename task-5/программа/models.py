class Flight:
    def __init__(self, number, destination, price, free_seats, status="расписание"):
        if not number.strip() or not destination.strip():
            raise ValueError("Номер рейса и направление не должны быть пустыми")
        if price < 0:
            raise ValueError("Стоимость билета не может быть отрицательной")
        if free_seats < 0:
            raise ValueError("Количество свободных мест не может быть отрицательным")
        self.number = number.strip().upper()
        self.destination = destination.strip()
        self.price = price
        self.free_seats = free_seats
        self.status = status.strip().lower()

    def __str__(self):
        return (f"{self.number} | {self.destination} | {self.price:.0f} руб. | "
                f"свободно: {self.free_seats} | {self.status}")

    def is_available(self):
        return self.status == "вылет" and self.free_seats > 0


class InternationalFlight(Flight):
    def __init__(self, number, destination, price, free_seats, status, country):
        super().__init__(number, destination, price, free_seats, status)
        self.country = country.strip()

    def __str__(self):
        return super().__str__() + f" | {self.country}"


class CharterFlight(Flight):
    def __init__(self, number, destination, price, free_seats, status, operator):
        super().__init__(number, destination, price, free_seats, status)
        self.operator = operator.strip()

    def __str__(self):
        return super().__str__() + f" | оператор: {self.operator}"
