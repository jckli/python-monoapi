from ...common.responses import error_response, json_response
from ..pixiv.client import aapi, authenticate_pixiv


async def get_illust_details_handler(illust_id):
    try:
        if not aapi.access_token:
            await authenticate_pixiv()
            if not aapi.access_token:
                return error_response(
                    "Pixiv authentication failed. Check your refresh token.", 500
                )

        json_result = await aapi.illust_detail(int(illust_id))

        if json_result.get("error"):
            error_message = (
                json_result["error"].get("user_message")
                or "Illustration not found or API error."
            )
            return error_response(error_message, 404)

        return json_response(json_result.get("illust", {}))

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return error_response("An internal server error occurred.", 500)
