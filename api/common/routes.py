from ..services.pixiv.routes import pixiv_routes
from .index import index


def init_routes(app):
    app.get("/", index)

    pixiv_routes(app.router("/pixiv"))


def register(router, path, handler_func):
    @router.get(path)
    async def wrapper(res, req):
        await handler_func(res, req)
