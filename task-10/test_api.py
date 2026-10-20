from app import API_KEY, create_app
from repository import CarRepository
from service import CarService


def setup():
    service = CarService(CarRepository())
    app = create_app(service)
    app.testing = True
    return app.test_client()


def headers():
    return {"X-API-Key": API_KEY}


def test_crud_lifecycle():
    client = setup()
    response = client.post("/cars", json={"make":"Toyota","model":"Camry","plate":"A1","category":"comfort"}, headers=headers())
    assert response.status_code == 201
    car_id = response.json["id"]
    assert client.get(f"/cars/{car_id}", headers=headers()).status_code == 200
    assert client.put(f"/cars/{car_id}", json={"make":"Toyota","model":"Prius","plate":"A2","category":"eco"}, headers=headers()).json["model"] == "Prius"
    assert client.patch(f"/cars/{car_id}", json={"available":False}, headers=headers()).json["available"] is False
    assert client.delete(f"/cars/{car_id}", headers=headers()).status_code == 204
    assert client.get(f"/cars/{car_id}", headers=headers()).status_code == 404


def test_available_endpoint_and_etag():
    client = setup()
    client.post("/cars", json={"make":"A","model":"B","plate":"1","category":"standard","available":True}, headers=headers())
    response = client.get("/cars/available", headers=headers())
    assert response.status_code == 200 and response.json["total"] == 1
    etag = response.headers["ETag"]
    cached = client.get("/cars/available", headers={**headers(), "If-None-Match": etag})
    assert cached.status_code == 304


def test_filters_sort_and_pagination():
    client = setup()
    for idx, category in enumerate(("comfort", "standard", "comfort")):
        client.post("/cars", json={"make":f"M{idx}","model":"X","plate":str(idx),"category":category,"available":idx != 1}, headers=headers())
    response = client.get("/cars?category=comfort&available=true&sort=make&order=desc&page=1&limit=1", headers=headers())
    assert response.status_code == 200 and response.json["total"] == 2 and len(response.json["items"]) == 1


def test_api_key_required():
    assert setup().get("/cars").status_code == 401


def test_validation_and_missing_resource():
    client = setup()
    assert client.post("/cars", json={"make":""}, headers=headers()).status_code == 400
    assert client.get("/cars/999", headers=headers()).status_code == 404


if __name__ == "__main__":
    tests = [value for name, value in globals().items() if name.startswith("test_")]
    for test in tests:
        test()
    print(f"Пройдено тестов: {len(tests)}")
