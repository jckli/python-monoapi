from .illust import get_illust_details
from .ugoira import get_ugoira_metadata


def register(router, path, handler_func):
    @router.get(path)
    async def wrapper(res, req):
        await handler_func(res, req)


def pixiv_routes(router):
    register(router, "/illust/:id", get_illust_details)
    register(router, "/ugoira/:id", get_ugoira_metadata)
