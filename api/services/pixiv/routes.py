from robyn import SubRouter

from ...common.responses import error_response
from .illust import get_illust_details_handler, get_illust_rank_handler
from .pximg import (
    get_random_ranking_api_handler,
    get_random_ranking_image_handler,
    pixiv_proxy_handler,
)
from .ugoira import get_ugoira_metadata_handler

pixiv_router = SubRouter(__file__, prefix="/v1/pixiv")


@pixiv_router.get("/illust/details/:id")
async def get_illust_details(request):
    illust_id = request.path_params.get("id")
    if not illust_id.isdigit():
        return error_response(
            "A valid illustration ID is required in the URL path. Example: /illust/details/123456789",
            400,
        )
    data = await get_illust_details_handler(int(illust_id))
    return data


@pixiv_router.get("/illust/ranking")
async def get_illust_ranking(request):
    mode = request.query_params.get("mode", "week")
    date = request.query_params.get("date", None)
    offset_str = request.query_params.get("offset", None)

    offset = None
    if offset_str:
        if not offset_str.isdigit():
            return error_response(
                "Query parameter 'offset' must be a valid number.",
                400,
            )
        offset = int(offset_str)

    data = await get_illust_rank_handler(mode=mode, date=date, offset=offset)
    return data


@pixiv_router.get("/ugoira_metadata/:id")
async def get_ugoira_metadata(request):
    illust_id = request.path_params.get("id")
    if not illust_id.isdigit():
        return error_response(
            "A valid illustration ID is required in the URL path. Example: /ugoira_metadata/123456789",
            400,
        )
    data = await get_ugoira_metadata_handler(int(illust_id))
    return data


@pixiv_router.get("/illust/proxy/*path")
async def proxy_pixiv_image(request):
    data = await pixiv_proxy_handler(request)
    return data


@pixiv_router.get("/illust/ranking/random/api")
async def get_random_ranking_api(request):
    data = await get_random_ranking_api_handler(request)
    return data


@pixiv_router.get("/illust/ranking/random/image")
async def get_random_ranking_image(request):
    data = await get_random_ranking_image_handler(request)
    return data
