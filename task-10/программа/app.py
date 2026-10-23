from flask import Flask, jsonify, make_response, request
from hashlib import sha256
import json
import logging
import time

from exceptions import CarNotFoundError, ValidationError
from repository import CarRepository
from service import CarService

API_KEY = "taxi-demo-key"


def create_app(service=None):
    app = Flask(__name__)
    app.config["SERVICE"] = service or CarService(CarRepository())
    svc: CarService = app.config["SERVICE"]

    @app.before_request
    def before_request():
        request.started_at = time.perf_counter()
        if request.path.startswith("/cars") and request.headers.get("X-API-Key") != API_KEY:
            return jsonify({"error": "Требуется корректный X-API-Key"}), 401

    @app.after_request
    def after_request(response):
        started = getattr(request, "started_at", time.perf_counter())
        logging.info("%s %s -> %s (%.2f ms)", request.method, request.path, response.status_code, (time.perf_counter() - started) * 1000)
        response.headers["X-Client-Version"] = "1.0"
        return response

    @app.errorhandler(CarNotFoundError)
    def not_found(error):
        return jsonify({"error": str(error)}), 404

    @app.errorhandler(ValidationError)
    @app.errorhandler(ValueError)
    def bad_request(error):
        return jsonify({"error": str(error)}), 400

    @app.get("/cars")
    def list_cars():
        category = request.args.get("category")
        raw_available = request.args.get("available")
        available = None
        if raw_available is not None:
            if raw_available.lower() not in {"true", "false"}:
                raise ValidationError("available должен быть true или false")
            available = raw_available.lower() == "true"
        min_id = int(request.args["min_id"]) if "min_id" in request.args else None
        max_id = int(request.args["max_id"]) if "max_id" in request.args else None
        cars = svc.list_cars(category, available, min_id, max_id, request.args.get("sort", "id"), request.args.get("order", "asc"))
        page = max(1, int(request.args.get("page", 1)))
        limit = min(100, max(1, int(request.args.get("limit", 20))))
        data = {"items": [car.to_dict() for car in cars[(page - 1) * limit:page * limit]], "page": page, "limit": limit, "total": len(cars)}
        return jsonify(data)

    @app.get("/cars/available")
    def available_cars():
        cars = svc.available_cars()
        payload = json.dumps([car.to_dict() for car in cars], sort_keys=True)
        etag = sha256(payload.encode()).hexdigest()
        if request.headers.get("If-None-Match", "").strip('"') == etag:
            return "", 304
        response = make_response(jsonify({"items": [car.to_dict() for car in cars], "total": len(cars)}))
        response.set_etag(etag)
        return response

    @app.get("/cars/<int:car_id>")
    def get_car(car_id):
        return jsonify(svc.get(car_id).to_dict())

    @app.post("/cars")
    def create_car():
        car = svc.create(request.get_json(silent=True) or {})
        return jsonify(car.to_dict()), 201

    @app.put("/cars/<int:car_id>")
    def replace_car(car_id):
        return jsonify(svc.replace(car_id, request.get_json(silent=True) or {}).to_dict())

    @app.patch("/cars/<int:car_id>")
    def patch_car(car_id):
        return jsonify(svc.patch(car_id, request.get_json(silent=True) or {}).to_dict())

    @app.delete("/cars/<int:car_id>")
    def delete_car(car_id):
        svc.delete(car_id)
        return "", 204

    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    application = create_app()
    application.run(host="127.0.0.1", port=5000, debug=False)
