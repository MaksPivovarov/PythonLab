def filter_objects(objects, predicate):
    return filter(predicate, objects)


def transform_objects(objects, operation):
    return map(operation, objects)


def sort_objects(objects, key_function):
    return sorted(objects, key=key_function)


def cheapest(objects):
    return min(objects, key=lambda obj: obj.price)


def has_destination(objects, destination):
    query = destination.casefold()
    return any(obj.destination.casefold() == query for obj in objects)


def all_positive_prices(objects):
    return all(obj.price >= 0 for obj in objects)


def average_price(objects):
    prices = [obj.price for obj in objects]
    if not prices:
        return 0
    return sum(prices) / len(prices)


def process_pipeline(objects, predicate, operation, key_function, available_predicate):
    pipeline = filter_objects(objects, predicate)
    pipeline = transform_objects(pipeline, operation)
    pipeline = sorted(pipeline, key=key_function)
    return (item for item in pipeline if available_predicate(item))
