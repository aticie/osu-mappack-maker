import asyncio
from typing import Union

import aiohttp

from mappacker.osu_api.base_api import BaseAPI
from mappacker.osu_models.chimu import ChimuBeatmapset
from mappacker.osu_models.nerinyan import NerinyanBeatmapset


class RippleAPI(BaseAPI):
    BASE_URL = "https://storage.ripple.moe/"
    DL_BEATMAP_PATH = "d/{}"
    SEMAPHORE = asyncio.Semaphore(2)

    async def get_beatmap(self, beatmap_id: Union[int, str]):
        return

    async def download_beatmapset(self, beatmapset: Union[NerinyanBeatmapset, ChimuBeatmapset], job_id: int) -> str:
        if beatmapset.ranked <= 0:
            raise aiohttp.ClientError()
        return await super(RippleAPI, self).download_beatmapset(beatmapset=beatmapset, job_id=job_id)
