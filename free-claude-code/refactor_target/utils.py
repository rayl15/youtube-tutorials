"""Pre-refactor: no logging. Demo task is to add it."""


def format_response(data, status=200):
    return {"status": status, "data": data}


def parse_query(query_string):
    parts = query_string.split("&")
    return {p.split("=")[0]: p.split("=")[1] for p in parts}
