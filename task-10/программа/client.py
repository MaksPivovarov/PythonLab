import json
import urllib.error
import urllib.request


class CarApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:5000", api_key: str = "taxi-demo-key") -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def request(self, method: str, path: str, data: dict | None = None) -> tuple[int, dict | str]:
        body = json.dumps(data).encode() if data is not None else None
        request = urllib.request.Request(self.base_url + path, data=body, method=method, headers={"X-API-Key": self.api_key, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request) as response:
                raw = response.read().decode()
                return response.status, json.loads(raw) if raw else ""
        except urllib.error.HTTPError as error:
            return error.code, error.read().decode()
