import asyncio
from typing import Union

import aiohttp

from osu_api.base_api import BaseAPI

ripple_semaphore = asyncio.Semaphore(2)


class RippleAPI(BaseAPI):
    BASE_URL = "https://storage.ripple.moe/"
    DL_BEATMAP_PATH = "d/{}"
    SEMAPHORE = ripple_semaphore

    def get_beatmap(self, beatmap_id: Union[int, str]):
        raise aiohttp.ClientError()
