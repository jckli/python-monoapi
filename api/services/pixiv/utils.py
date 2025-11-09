import logging
import random
from datetime import datetime, timedelta

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


def _get_random_ranking_params(request_params):
    mode = request_params.get("mode", None)
    if not mode:
        mode = random.choice(["day", "week", "month"])

    date = request_params.get("date", None)
    if not date:
        random_days = random.randint(1, 730)
        date = (datetime.now() - timedelta(days=random_days)).strftime("%Y-%m-%d")

    nsfw = request_params.get("nsfw", "false")

    return mode, date, nsfw
