"""Pre-refactor: no logging. Demo task is to add it."""

_DB = {}


def get(key):
    return _DB.get(key)


def set(key, value):
    _DB[key] = value
    return value
