from robyn import Robyn

from api.common.auth_services import authenticate_services
from api.common.routes import init_routes

app = Robyn(__file__)
init_routes(app)


@app.startup_handler
async def startup():
    print("Server starting up...")
    await authenticate_services()
    print("Startup complete. Ready to accept requests.")


if __name__ == "__main__":
    print("Preparing to listen on port 3000")
    app.start(host="0.0.0.0", port=3000)
