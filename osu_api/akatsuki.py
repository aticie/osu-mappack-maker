import asyncio
from typing import Union

import aiohttp

from osu_api.base_api import BaseAPI

akatsuki_semaphore = asyncio.Semaphore(2)


class AkatsukiAPI(BaseAPI):
    BASE_URL = "https://akatsuki.gg/"
    DL_BEATMAP_PATH = "d/{}"
    SEMAPHORE = akatsuki_semaphore

    def get_beatmap(self, beatmap_id: Union[int, str]):
        raise aiohttp.ClientError()
