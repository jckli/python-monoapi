import asyncio

from socketify import App

from api.common.routes import init_routes

app = App()


async def startup():
    print("Server starting up...")
    print("Startup complete. Ready to accept requests.")


init_routes(app)


if __name__ == "__main__":
    asyncio.run(startup())
    app.listen(
        3000,
        lambda config: print(f"Listening on port: {config.port}"),
    )
    app.run()
