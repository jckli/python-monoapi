from ...common.responses import error_response, json_response
from ..pixiv.client import aapi, authenticate_pixiv


async def get_illust_details(res, req):
    res.on_aborted(lambda: res.aborted())

    illust_id = req.get_query("id")

    if not illust_id or not illust_id.isdigit():
        return error_response(
            res, "A valid illustration ID is required. Example: /illust?id=12345", 400
        )

    try:
        if not aapi.access_token:
            await authenticate_pixiv()
            if not aapi.access_token:
                return error_response(
                    res, "Pixiv authentication failed. Check your refresh token.", 500
                )

        json_result = await aapi.illust_detail(int(illust_id))

        if json_result.get("error"):
            error_message = (
                json_result["error"].get("user_message")
                or "Illustration not found or API error."
            )
            return error_response(res, error_message, 404)

        # Success
        json_response(res, json_result.get("illust", {}))

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        error_response(res, "An internal server error occurred.", 500)
