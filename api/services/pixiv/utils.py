import logging

from ...common.responses import error_response
from ..pixiv.client import aapi, authenticate_pixiv

logger = logging.getLogger(__name__)


async def _ensure_pixiv_auth(is_retry: bool = False):
    if not aapi.access_token:
        log_prefix = "Re-" if is_retry else "Initial"
        log_message = (
            "Refreshing token..."
            if is_retry
            else "No Pixiv access token. Authenticating..."
        )
        logger.info(log_message)

        await authenticate_pixiv()

        if not aapi.access_token:
            logger.error(
                f"{log_prefix}Pixiv authentication failed. Check refresh token."
            )
            return error_response(
                f"Pixiv {log_prefix.lower()}authentication failed.", 500
            )
    return None
