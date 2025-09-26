from .responses import generic_response


def index(res, _):
    generic_response(res, "welcome to jckli/python-monoapis v1")
