import os

from dotenv import load_dotenv
from pixivpy_async import AppPixivAPI

load_dotenv()
PIXIV_REFRESH_TOKEN = os.getenv("PIXIV_REFRESH_TOKEN")

aapi = AppPixivAPI()


async def authenticate_pixiv():
    try:
        if PIXIV_REFRESH_TOKEN:
            await aapi.login(refresh_token=PIXIV_REFRESH_TOKEN)
            return True
        else:
            print("PIXIV_REFRESH_TOKEN not found. Please set it in your .env file.")
            return False
    except Exception as e:
        print(f"Error during Pixiv authentication: {e}")
        return False


async def startup_authenticate_pixiv():
    print("Authenticating with Pixiv...")
    if await authenticate_pixiv():
        print("Successfully authenticated with Pixiv using refresh token.")
