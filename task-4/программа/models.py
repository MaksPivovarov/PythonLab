class Flight:
    def __init__(self, number, destination, departure, arrival, seats, booked=0):
        if not number.strip() or not destination.strip():
            raise ValueError("Номер рейса и направление не должны быть пустыми")
        if seats < 1 or booked < 0 or booked > seats:
            raise ValueError("Некорректное количество мест или бронирований")
        self.number = number.strip().upper()
        self.destination = destination.strip()
        self.departure = departure.strip()
        self.arrival = arrival.strip()
        self.seats = seats
        self.booked = booked

    @property
    def free_seats(self):
        return self.seats - self.booked

    def book_seat(self):
        if self.free_seats == 0:
            from exceptions import NoSeatsAvailableError
            raise NoSeatsAvailableError(f"На рейсе {self.number} нет свободных мест")
        self.booked += 1

    def cancel_booking(self):
        if self.booked == 0:
            raise ValueError("Для этого рейса нет бронирований")
        self.booked -= 1

    def to_dict(self):
        return {
            "number": self.number,
            "destination": self.destination,
            "departure": self.departure,
            "arrival": self.arrival,
            "seats": self.seats,
            "booked": self.booked,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["number"], data["destination"], data["departure"],
            data["arrival"], int(data["seats"]), int(data.get("booked", 0))
        )

    def __str__(self):
        return (f"{self.number} | {self.destination} | {self.departure}-{self.arrival} | "
                f"свободно {self.free_seats}/{self.seats}")
