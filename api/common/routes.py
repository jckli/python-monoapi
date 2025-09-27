from ..services.pixiv.routes import pixiv_routes
from .index import index


def init_routes(app):
    app.get("/", index)

    pixiv_routes(app.router("/v1/pixiv"))
