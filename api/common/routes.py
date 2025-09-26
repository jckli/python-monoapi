from .index import index


def init_routes(app):
    app.get("/", index)
