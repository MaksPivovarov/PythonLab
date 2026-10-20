from typing import Protocol


class Reportable(Protocol):
    def report(self) -> str:
        ...


def print_report(item: Reportable) -> None:
    print(item.report())
