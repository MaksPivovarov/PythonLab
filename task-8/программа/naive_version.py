from models import Ride


class NaiveTaxiCalculator:
    def calculate(self, distance_km: float, car_type: str, tariff: str) -> float:
        if tariff == "ночной":
            base, rate = 130, 52
        elif tariff == "повышенный":
            base, rate = 150, 60
        else:
            base, rate = 100, 40
        if car_type == "комфорт":
            multiplier = 1.3
        elif car_type == "бизнес":
            multiplier = 1.8
        else:
            multiplier = 1.0
        return (base + distance_km * rate) * multiplier
