from functools import wraps
from time import perf_counter
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def log_call(function: F) -> F:
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"[LOG] {function.__name__} args={args[1:]}, kwargs={kwargs}")
        result = function(*args, **kwargs)
        print(f"[LOG] {function.__name__} -> {result}")
        return result
    return wrapper  # type: ignore[return-value]


def measure_time(function: F) -> F:
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        started = perf_counter()
        try:
            return function(*args, **kwargs)
        finally:
            print(f"[PERFORMANCE] {function.__name__}: {perf_counter() - started:.6f} sec")
    return wrapper  # type: ignore[return-value]


def command(title: str) -> Callable[[F], F]:
    def decorate(function: F) -> F:
        setattr(function, "command_title", title)
        return function
    return decorate


def require_status(*allowed: Any) -> Callable[[F], F]:
    def decorate(function: F) -> F:
        @wraps(function)
        def wrapper(self: Any, ride_id: int, *args: Any, **kwargs: Any) -> Any:
            ride = self.registry.find(ride_id)
            if ride is None:
                raise LookupError(f"Поездка #{ride_id} не найдена")
            if ride.status not in allowed:
                raise ValueError(f"Недопустимый статус поездки: {ride.status}")
            return function(self, ride_id, *args, **kwargs)
        return wrapper  # type: ignore[return-value]
    return decorate
