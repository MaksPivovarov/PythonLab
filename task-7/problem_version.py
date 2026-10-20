from models import Driver, Ride, RideStatus


class BadTaxiApp:
    def __init__(self) -> None:
        self.rides: list[Ride] = []
        self.drivers = [Driver(1, "Иван"), Driver(2, "Анна")]

    def create_assign_start_finish(self) -> None:
        passenger = input("Пассажир: ")
        distance = float(input("Расстояние: "))
        ride = Ride(len(self.rides) + 1, passenger, distance)
        ride.driver = self.drivers[0]
        ride.status = RideStatus.ASSIGNED
        ride.status = RideStatus.STARTED
        ride.price = 100 + distance * 45
        ride.status = RideStatus.COMPLETED
        self.rides.append(ride)
        print(ride)

    def report_and_save(self) -> None:
        print("Средняя стоимость:", sum(ride.price for ride in self.rides) / len(self.rides))


if __name__ == "__main__":
    BadTaxiApp().create_assign_start_finish()
