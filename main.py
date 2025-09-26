import asyncio

from socketify import App

from api.common.auth_services import authenticate_services
from api.common.routes import init_routes

app = App()


async def startup():
    print("Server starting up...")
    init_routes(app)
    await authenticate_services()
    print("Startup complete. Ready to accept requests.")


if __name__ == "__main__":
    asyncio.run(startup())
    app.listen(
        3000,
        lambda config: print(f"Listening on port: {config.port}"),
    )
    app.run()
