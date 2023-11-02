import asyncio
from typing import Union

import aiohttp

from osu_api.base_api import BaseAPI
from osu_models.chimu import ChimuBeatmapset
from osu_models.nerinyan import NerinyanBeatmapset

ripple_semaphore = asyncio.Semaphore(2)


class RippleAPI(BaseAPI):
    BASE_URL = "https://storage.ripple.moe/"
    DL_BEATMAP_PATH = "d/{}"
    SEMAPHORE = ripple_semaphore

    def get_beatmap(self, beatmap_id: Union[int, str]):
        raise aiohttp.ClientError()

    def download_beatmapset(self, beatmapset: Union[NerinyanBeatmapset, ChimuBeatmapset], job_id: int) -> str:
        if beatmapset.ranked <= 0:
            raise aiohttp.ClientError()
        super().download_beatmapset(beatmapset=beatmapset, job_id=job_id)
