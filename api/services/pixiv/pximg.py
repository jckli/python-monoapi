import logging
import random

import aiohttp
from robyn import Response

from ...common.responses import error_response, json_response
from ..pixiv.client import aapi, authenticate_pixiv
from ..pixiv.utils import _ensure_pixiv_auth, _get_random_ranking_params

logger = logging.getLogger(__name__)

PIXIV_BASE_URL = "https://i.pximg.net"
PIXIV_REFERER = "https://www.pixiv.net/"


async def pixiv_proxy_handler(request):
    try:
        pixiv_path = request.path_params.get("path")

        url = f"{PIXIV_BASE_URL}/{pixiv_path}"
        headers = {
            "Referer": PIXIV_REFERER,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as stream_resp:
                if stream_resp.status != 200:
                    logger.warning(
                        f"Pixiv proxy request failed for {pixiv_path} with status {stream_resp.status}"
                    )
                    return Response(
                        status_code=stream_resp.status,
                        headers={"Content-Type": "text/plain"},
                        description=f"Error fetching from upstream: {stream_resp.status}",  # Using description
                    )

                content_type = stream_resp.headers.get(
                    "content-type", "application/octet-stream"
                )

                image_bytes = await stream_resp.read()

                return Response(
                    status_code=200,
                    headers={"Content-Type": content_type},
                    description=image_bytes,
                )

    except Exception as e:
        logger.error(
            f"An unexpected error occurred in proxy handler: {e}", exc_info=True
        )
        return Response(
            status_code=500,
            headers={"Content-Type": "text/plain"},
            description="An internal server error occurred.",
        )


async def _get_random_illust_from_ranking(mode, date, nsfw_flag):
    try:
        if auth_error := await _ensure_pixiv_auth():
            return None, auth_error

        json_result = await aapi.illust_ranking(mode=mode, date=date)

        if (error := json_result.get("error")) and "invalid_grant" in error.get(
            "message", ""
        ):
            logger.info("Pixiv token invalid/expired. Refreshing and retrying.")
            await authenticate_pixiv()
            if not aapi.access_token:
                logger.error("Pixiv re-authentication failed.")
                return None, error_response("Pixiv re-authentication failed.", 500)
            json_result = await aapi.illust_ranking(mode=mode, date=date)

        if final_error := json_result.get("error"):
            logger.warning(f"Pixiv API error on ranking: {final_error}")
            return None, error_response("Error fetching rankings.", 404)

        all_illusts = json_result.get("illusts")
        if not all_illusts:
            logger.warning("No illusts found in ranking response.")
            return None, error_response("No illustrations found for ranking.", 404)

        available_illusts = []
        if nsfw_flag == "only":
            available_illusts = [
                i for i in all_illusts if i.get("sanity_level", 0) >= 5
            ]
        elif nsfw_flag == "true":
            available_illusts = all_illusts
        else:
            available_illusts = [i for i in all_illusts if i.get("sanity_level", 0) < 5]

        if not available_illusts:
            logger.warning(
                f"No results for nsfw='{nsfw_flag}', falling back to all illusts."
            )
            available_illusts = all_illusts

        illust = random.choice(available_illusts)
        is_nsfw = illust.get("sanity_level", 0) >= 5
        image_url = ""

        if illust.get("meta_pages") and len(illust["meta_pages"]) > 0:
            page = random.choice(illust["meta_pages"])
            image_url = page.get("image_urls", {}).get("original")
        else:
            image_url = illust.get("meta_single_page", {}).get("original_image_url")

        if not image_url:
            logger.error(f"Illust {illust.get('id')} had no image URL.")
            return None, error_response("Selected illust had no image URL.", 500)

        return image_url, is_nsfw

    except Exception as e:
        logger.error(
            f"An unexpected error occurred in _get_random_illust: {e}", exc_info=True
        )
        return None, error_response("An internal server error occurred.", 500)


async def get_random_ranking_api_handler(request):
    query_params = request.query_params
    mode, date, nsfw_flag = _get_random_ranking_params(query_params)

    image_url, result = await _get_random_illust_from_ranking(mode, date, nsfw_flag)

    if image_url is None:
        return result

    if "https://i.pximg.net/" not in image_url:
        logger.error(f"Illust URL was not a valid i.pximg.net URL: {image_url}")
        return error_response("Invalid image URL from Pixiv.", 500)

    image_path = image_url.split("https://i.pximg.net/")[-1]

    return json_response(
        {"status": 200, "data": {"illust_path": image_path, "nsfw": result}}
    )


async def get_random_ranking_image_handler(request):
    query_params = request.query_params
    mode, date, nsfw_flag = _get_random_ranking_params(query_params)

    image_url, result = await _get_random_illust_from_ranking(mode, date, nsfw_flag)

    if image_url is None:
        return result

    if "https://i.pximg.net/" not in image_url:
        logger.error(f"Illust URL was not a valid i.pximg.net URL: {image_url}")
        return error_response("Invalid image URL from Pixiv.", 500)

    image_path = image_url.split("https://i.pximg.net/")[-1]

    return Response(
        status_code=302,
        headers={"Location": f"/v1/pixiv/illust/proxy/{image_path}"},
        description="",
    )
