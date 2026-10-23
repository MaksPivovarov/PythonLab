import json
import socket
import uuid

from server import HOST, PORT


class CarClient:
    def __init__(self, host: str = HOST, port: int = PORT) -> None:
        self.host = host
        self.port = port
        self.connection: socket.socket | None = None
        self.reader = None

    def connect(self) -> None:
        self.connection = socket.create_connection((self.host, self.port), timeout=5)
        self.reader = self.connection.makefile("r", encoding="utf-8")

    def send(self, command: str, data: dict | None = None) -> dict:
        if self.connection is None or self.reader is None:
            raise ConnectionError("Сначала подключитесь к серверу")
        request_id = str(uuid.uuid4())
        request = {"request_id": request_id, "command": command, "data": data or {}}
        self.connection.sendall((json.dumps(request, ensure_ascii=False) + "\n").encode("utf-8"))
        response = json.loads(self.reader.readline())
        if response.get("request_id") != request_id:
            raise ConnectionError("Идентификатор ответа не совпал с запросом")
        return response

    def close(self) -> None:
        if self.reader:
            self.reader.close()
        if self.connection:
            self.connection.close()


def main() -> None:
    client = CarClient()
    try:
        client.connect()
        while True:
            print("\n1.Список 2.Получить 3.Создать 4.Изменить 5.Удалить 6.Свободные 7.Ping 8.История 0.Выход")
            choice = input("Команда: ").strip()
            try:
                if choice == "0":
                    break
                if choice == "1":
                    response = client.send("list")
                elif choice == "2":
                    response = client.send("get", {"id": int(input("ID: "))})
                elif choice == "3":
                    response = client.send("create", {"make": input("Марка: "), "model": input("Модель: "), "plate": input("Номер: ")})
                elif choice == "4":
                    response = client.send("update", {"id": int(input("ID: ")), "available": input("Свободна? (y/n): ").lower() == "y"})
                elif choice == "5":
                    response = client.send("delete", {"id": int(input("ID: "))})
                elif choice == "6":
                    response = client.send("available_cars")
                elif choice == "7":
                    response = client.send("ping")
                elif choice == "8":
                    response = client.send("history")
                else:
                    print("Неизвестный пункт.")
                    continue
                print(json.dumps(response, ensure_ascii=False, indent=2))
            except (ValueError, OSError, ConnectionError) as error:
                print("Ошибка:", error)
    except OSError as error:
        print(f"Не удалось подключиться к серверу: {error}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
