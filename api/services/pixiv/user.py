import logging

from ...common.responses import error_response, json_response
from ..pixiv.client import aapi, authenticate_pixiv
from ..pixiv.utils import _ensure_pixiv_auth

logger = logging.getLogger(__name__)


async def get_user_details_handler(user_id):
    try:
        if auth_error := await _ensure_pixiv_auth():
            return auth_error

        json_result = await aapi.user_detail(int(user_id))

        if (error := json_result.get("error")) and "invalid_grant" in error.get(
            "message", ""
        ):
            logger.info("Pixiv token invalid/expired. Refreshing and retrying.")
            await authenticate_pixiv()
            if not aapi.access_token:
                logger.error("Pixiv re-authentication failed. Check refresh token.")
                return error_response("Pixiv re-authentication failed.", 500)

            json_result = await aapi.user_detail(int(user_id))

        if final_error := json_result.get("error"):
            logger.warning(f"Pixiv API error: {final_error}")
            error_message = (
                final_error.get("user_message")
                or "User not found or API error."
            )
            return error_response(error_message, 404)

        return json_response(json_result)

    except Exception as e:
        logger.error(f"An unexpected error occurred in user details handler: {e}", exc_info=True)
        return error_response("An internal server error occurred.", 500)


async def get_user_illusts_handler(user_id, illust_type="illust"):
    try:
        if auth_error := await _ensure_pixiv_auth():
            return auth_error

        json_result = await aapi.user_illusts(int(user_id), type=illust_type)

        if (error := json_result.get("error")) and "invalid_grant" in error.get(
            "message", ""
        ):
            logger.info("Pixiv token invalid/expired. Refreshing and retrying.")
            await authenticate_pixiv()
            if not aapi.access_token:
                logger.error("Pixiv re-authentication failed. Check refresh token.")
                return error_response("Pixiv re-authentication failed.", 500)

            json_result = await aapi.user_illusts(int(user_id), type=illust_type)

        if final_error := json_result.get("error"):
            logger.warning(f"Pixiv API error: {final_error}")
            error_message = (
                final_error.get("user_message")
                or "Error fetching user illusts or API error."
            )
            return error_response(error_message, 404)

        if "illusts" in json_result:
            return json_response(json_result.get("illusts", []))

        return json_response(json_result)

    except Exception as e:
        logger.error(f"An unexpected error occurred in user illusts handler: {e}", exc_info=True)
        return error_response("An internal server error occurred.", 500)
