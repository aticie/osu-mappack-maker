import asyncio
import logging
from typing import Union
from urllib.parse import urljoin

import aiohttp

from mappacker.osu_api.base_api import BaseAPI
from mappacker.osu_models.nerinyan import NerinyanBeatmap, NerinyanBeatmapset
from mappacker.utils.aiohttp import SingletonAiohttp

logger = logging.getLogger(__name__)


class NerinyanAPI(BaseAPI):
    BASE_URL = "https://api.nerinyan.moe/"
    GET_BEATMAP_PATH = "search"
    DL_BEATMAP_PATH = "d/{}"
    SEMAPHORE = asyncio.Semaphore(50)
    BEATMAP_CLASS = NerinyanBeatmap
    BEATMAPSET_CLASS = NerinyanBeatmapset

    async def get_beatmap(self, beatmap_id: Union[str, int]):
        sess = SingletonAiohttp.get_aiohttp_client()
        params = {"q": beatmap_id,
                  "option": "mapId",
                  "s": "-2,-1,0,1,2,3,4"}
        url = urljoin(self.BASE_URL, self.GET_BEATMAP_PATH)
        logger.info(f"Getting beatmap info: {url} with from {self.__class__.__name__} with {params=}.")
        async with sess.get(url, params=params) as r:
            if r.status != 200:
                raise aiohttp.ClientError()
            response = await r.json()
            logger.debug(f"Response received for {url} with {params=}: {response}")

        if len(response) == 0:
            logger.info(f"{beatmap_id} search returned 0 result.")
            raise aiohttp.ClientError()
        logger.info(f"Got the beatmap for {beatmap_id}.")
        return self.BEATMAPSET_CLASS(**response[0])
