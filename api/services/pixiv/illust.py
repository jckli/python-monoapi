import logging

from ...common.responses import error_response, json_response
from ..pixiv.client import aapi, authenticate_pixiv
from ..pixiv.utils import _ensure_pixiv_auth

logger = logging.getLogger(__name__)


async def get_illust_details_handler(illust_id):
    try:
        if auth_error := await _ensure_pixiv_auth():
            return auth_error

        json_result = await aapi.illust_detail(int(illust_id))

        if (error := json_result.get("error")) and "invalid_grant" in error.get(
            "message", ""
        ):
            logger.info("Pixiv token invalid/expired. Refreshing and retrying.")
            await authenticate_pixiv()
            if not aapi.access_token:
                logger.error("Pixiv re-authentication failed. Check refresh token.")
                return error_response("Pixiv re-authentication failed.", 500)

            json_result = await aapi.illust_detail(int(illust_id))

        if final_error := json_result.get("error"):
            logger.warning(f"Pixiv API error: {final_error}")
            error_message = (
                final_error.get("user_message")
                or "Illustration not found or API error."
            )
            return error_response(error_message, 404)

        if illust := json_result.get("illust"):
            return json_response(illust)

        logger.error(f"Unexpected Pixiv API response format: {json_result}")
        return error_response("Unexpected API response from Pixiv.", 500)

    except Exception as e:
        logger.error(f"An unexpected error occurred in handler: {e}", exc_info=True)
        return error_response("An internal server error occurred.", 500)
