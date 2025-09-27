from ...common.responses import error_response, json_response
from ..pixiv.client import aapi, authenticate_pixiv


async def get_ugoira_metadata(res, req):
    res.on_aborted(lambda: res.aborted())

    illust_id = req.get_parameter(0)

    if not illust_id or not illust_id.isdigit():
        return error_response(
            res,
            "A valid illustration ID is required. Example: /ugoira/metadata?id=12345",
            400,
        )

    try:
        if not aapi.access_token:
            await authenticate_pixiv()
            if not aapi.access_token:
                return error_response(
                    res, "Pixiv authentication failed. Check your refresh token.", 500
                )

        json_result = await aapi.ugoira_metadata(int(illust_id))

        if json_result.get("error"):
            error_message = (
                json_result["error"].get("user_message")
                or "Ugoira metadata not found or API error."
            )
            return error_response(res, error_message, 404)

        json_response(res, json_result.get("ugoira_metadata", {}))

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        error_response(res, "An internal server error occurred.", 500)
