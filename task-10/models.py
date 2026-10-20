from dataclasses import asdict, dataclass


@dataclass
class Car:
    id: int
    make: str
    model: str
    plate: str
    category: str
    available: bool = True
    driver: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
