from dataclasses import asdict, dataclass


@dataclass
class Car:
    id: int
    make: str
    model: str
    plate: str
    available: bool = True

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Car":
        return cls(int(data["id"]), str(data["make"]), str(data["model"]), str(data["plate"]), bool(data.get("available", True)))
