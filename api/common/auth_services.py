from ..services.pixiv.client import startup_authenticate_pixiv


async def authenticate_services():
    await startup_authenticate_pixiv()
