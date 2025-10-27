from ..services.pixiv.routes import pixiv_router
from .index import index


def init_routes(app):
    app.add_route(route_type="GET", endpoint="/", handler=index)

    app.include_router(pixiv_router)
