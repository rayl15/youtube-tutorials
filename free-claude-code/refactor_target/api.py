"""Pre-refactor: no logging. Demo task is to add it."""

from auth import login, logout
from db import get, set


def handle_login(body):
    return login(body["username"], body["password"])


def handle_save(body):
    return set(body["key"], body["value"])


def handle_fetch(body):
    return get(body["key"])
