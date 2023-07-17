import asyncio

from osu_api.base_api import BaseAPI
from osu_api.direct import DirectBeatmap

catboy_semaphore = asyncio.Semaphore(1)


class CatboyAPI(BaseAPI):
    BASE_URL = "https://catboy.best/"
    GET_BEATMAP_PATH = "api/b/{}"
    DL_BEATMAP_PATH = "d/{}"
    SEMAPHORE = catboy_semaphore
    BEATMAP_CLASS = DirectBeatmap
