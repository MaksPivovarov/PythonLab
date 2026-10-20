from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any


class OperationLogger:
    def __init__(self, operation: str, parameters: Any = None, path: str = "operations.log") -> None:
        self.operation = operation
        self.parameters = parameters
        self.path = Path(path)
        self.started = 0.0
        self.result = "SUCCESS"
        self.exception: BaseException | None = None

    def __enter__(self) -> "OperationLogger":
        self.started = perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        duration = perf_counter() - self.started
        if exc_type is not None:
            self.result = "ERROR"
            self.exception = exc_value
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}]\n")
            file.write(f"Operation: {self.operation}\n")
            file.write(f"Parameters: {self.parameters}\n")
            file.write(f"Duration: {duration:.6f} sec\n")
            file.write(f"Result: {self.result}\n")
            if self.exception is not None:
                file.write(f"Exception: {type(self.exception).__name__}: {self.exception}\n")
            file.write("\n")
        return False
