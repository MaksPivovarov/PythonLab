import csv
import json
import os
import shutil

from models import Flight


class Repository:
    def save(self, objects):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError


class JsonRepository(Repository):
    def __init__(self, path):
        self.path = path
        self.backup_path = path + ".bak"

    def save(self, objects):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if os.path.exists(self.path):
            shutil.copy2(self.path, self.backup_path)
        temporary = self.path + ".tmp"
        with open(temporary, "w", encoding="utf-8") as file:
            json.dump([item.to_dict() for item in objects], file, ensure_ascii=False, indent=4)
        os.replace(temporary, self.path)

    def load(self):
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("JSON должен содержать список рейсов")
        return [Flight.from_dict(item) for item in data]

    def export_csv(self, objects, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fields = ("number", "destination", "departure", "arrival", "seats", "booked")
        with open(path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(item.to_dict() for item in objects)

    def import_csv(self, path):
        with open(path, "r", newline="", encoding="utf-8-sig") as file:
            return [Flight.from_dict(row) for row in csv.DictReader(file)]
