import asyncio
from typing import Union

import aiohttp

from osu_api.base_api import BaseAPI

gatari_semaphore = asyncio.Semaphore(2)


class GatariAPI(BaseAPI):
    BASE_URL = "https://osu.gatari.pw/"
    DL_BEATMAP_PATH = "d/{}"
    SEMAPHORE = gatari_semaphore

    def get_beatmap(self, beatmap_id: Union[int, str]):
        raise aiohttp.ClientError()
