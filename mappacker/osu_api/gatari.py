import asyncio
from typing import Union

from mappacker.osu_api.base_api import BaseAPI


class GatariAPI(BaseAPI):
    BASE_URL = "https://osu.gatari.pw/"
    DL_BEATMAP_PATH = "d/{}"
    SEMAPHORE = asyncio.Semaphore(2)

    async def get_beatmap(self, beatmap_id: Union[int, str]):
        return
