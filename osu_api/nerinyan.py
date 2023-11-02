import asyncio
import logging
from typing import Union
from urllib.parse import urljoin

import aiohttp

from osu_api.base_api import BaseAPI
from osu_models.nerinyan import NerinyanBeatmap, NerinyanBeatmapset

logger = logging.getLogger(__name__)

nerinyan_semaphore = asyncio.Semaphore(50)


class NerinyanAPI(BaseAPI):
    BASE_URL = "https://api.nerinyan.moe/"
    GET_BEATMAP_PATH = "search"
    DL_BEATMAP_PATH = "d/{}"
    SEMAPHORE = nerinyan_semaphore
    BEATMAP_CLASS = NerinyanBeatmap
    BEATMAPSET_CLASS = NerinyanBeatmapset

    async def get_beatmap(self, beatmap_id: Union[str, int]):
        async with nerinyan_semaphore:
            async with aiohttp.ClientSession() as sess:
                logger.info(f"Getting beatmap for {beatmap_id} from {self.__class__.__name__}.")
                params = {"q": beatmap_id,
                          "option": "mapId",
                          "s": "-2,-1,0,1,2,3,4"}
                url = urljoin(self.BASE_URL, self.GET_BEATMAP_PATH)
                async with sess.get(url, params=params) as r:
                    if r.status != 200:
                        raise aiohttp.ClientError()
                    response = await r.json()

                if len(response) == 0:
                    logger.info(f"{beatmap_id} search returned 0 result.")
                    raise aiohttp.ClientError()
                logger.info(f"Got the beatmap for {beatmap_id}.")
                return self.BEATMAP_CLASS(**response[0])
