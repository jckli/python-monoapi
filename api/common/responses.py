import json

from robyn import Response


def json_response(data: dict | list, status_code: int = 200) -> Response:
    return Response(
        status_code=status_code,
        description=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )


def generic_response(message: str, status_code: int = 200) -> Response:
    """
    Creates a Robyn generic message response.
    """
    payload = {"status": status_code, "message": message}
    return json_response(payload, status_code)


def error_response(message: str, status_code: int) -> Response:
    """
    Creates a Robyn error response.
    """
    payload = {"status": status_code, "error": message}
    return json_response(payload, status_code)
