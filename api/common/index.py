from .responses import generic_response


async def index():
    return generic_response("welcome to jckli/python-monoapi v1")
