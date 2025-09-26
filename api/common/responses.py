import json


def json_response(res, data, status_code=200):
    res.write_status(status_code)
    res.write_header("Content-Type", "application/json")
    res.end(json.dumps(data))


def generic_response(res, message, status_code=200):
    payload = {"status": status_code, "message": message}
    json_response(res, payload, status_code)


def error_response(res, message, status_code):
    payload = {"status": status_code, "error": message}
    json_response(res, payload, status_code)
