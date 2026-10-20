from abc import ABC, abstractmethod
from collections import Counter
from copy import deepcopy
from models import Ride, RideStatus


class Observer(ABC):
    @abstractmethod
    def update(self, event: str, ride: Ride) -> None:
        ...


class LogObserver(Observer):
    def __init__(self) -> None:
        self.events: list[str] = []

    def update(self, event: str, ride: Ride) -> None:
        self.events.append(f"{event}: {ride.id}")
        print(f"[LOG] {event} для заказа #{ride.id}")


class NotificationObserver(Observer):
    def update(self, event: str, ride: Ride) -> None:
        print(f"[NOTIFY] Пассажир {ride.passenger}: {event}")


class StatisticsObserver(Observer):
    def __init__(self) -> None:
        self.events = Counter()

    def update(self, event: str, ride: Ride) -> None:
        self.events[event] += 1


class RideSubject:
    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def notify(self, event: str, ride: Ride) -> None:
        for observer in self._observers:
            observer.update(event, ride)


class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...


class CreateRideCommand(Command):
    def __init__(self, service, ride: Ride) -> None:
        self.service = service
        self.ride = ride

    def execute(self) -> None:
        self.service.repository.add(self.ride)
        self.service.subject.notify("создание заказа", self.ride)

    def undo(self) -> None:
        self.service.repository.delete(self.ride.id)


class CommandHistory:
    def __init__(self) -> None:
        self._commands: list[Command] = []

    def execute(self, command: Command) -> None:
        command.execute()
        self._commands.append(command)

    def undo(self) -> None:
        if not self._commands:
            raise ValueError("История команд пуста")
        self._commands.pop().undo()
