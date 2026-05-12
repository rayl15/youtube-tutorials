"""Pre-refactor: no logging. Demo task is to add it."""


def login(username, password):
    if username == "admin" and password == "secret":
        return {"token": "abc123"}
    raise ValueError("invalid credentials")


def logout(token):
    return {"status": "logged_out"}
