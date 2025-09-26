from .responses import generic_response


async def index(res, _):
    generic_response(res, "welcome to jckli/python-monoapis v1")
