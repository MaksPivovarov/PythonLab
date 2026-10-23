from exceptions import FlightNotFoundError
from models import Flight


class FlightService:
    def __init__(self, repository, logger):
        self.repository = repository
        self.logger = logger
        self.flights = self.repository.load()

    def _log(self, message):
        self.logger(message)

    def add(self, flight):
        if any(item.number == flight.number for item in self.flights):
            raise ValueError("Рейс с таким номером уже существует")
        self.flights.append(flight)
        self.save()
        self._log(f"Добавлен рейс {flight.number}")

    def get(self, number):
        for flight in self.flights:
            if flight.number == number.strip().upper():
                return flight
        raise FlightNotFoundError(f"Рейс {number} не найден")

    def find_by_destination(self, destination):
        query = destination.casefold()
        return [item for item in self.flights if query in item.destination.casefold()]

    def book(self, number):
        flight = self.get(number)
        flight.book_seat()
        self.save()
        self._log(f"Забронировано место на рейсе {flight.number}")

    def cancel(self, number):
        flight = self.get(number)
        flight.cancel_booking()
        self.save()
        self._log(f"Отменено бронирование на рейсе {flight.number}")

    def save(self):
        self.repository.save(self.flights)

    def export_csv(self, path):
        self.repository.export_csv(self.flights, path)
        self._log(f"Выполнен экспорт в {path}")
