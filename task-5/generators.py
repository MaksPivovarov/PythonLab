class FlightIterator:
    def __init__(self, flights):
        self._flights = flights
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._flights):
            raise StopIteration
        flight = self._flights[self._index]
        self._index += 1
        return flight


def flights_with_seats(flights):
    for flight in flights:
        if flight.free_seats > 0:
            yield flight


def flights_to_destination(flights, destination):
    query = destination.casefold()
    for flight in flights:
        if flight.destination.casefold() == query:
            yield flight
