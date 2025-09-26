from .illust import get_illust_details


def register(router, path, handler_func):
    @router.get(path)
    async def wrapper(res, req):
        await handler_func(res, req)


def pixiv_routes(router):
    register(router, "/illust", get_illust_details)
