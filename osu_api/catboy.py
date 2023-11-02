import asyncio

from osu_models.chimu import ChimuBeatmap, ChimuBeatmapset
from osu_api.base_api import BaseAPI

catboy_semaphore = asyncio.Semaphore(1)


class CatboyAPI(BaseAPI):
    BASE_URL = "https://catboy.best/"
    GET_BEATMAP_PATH = "api/b/{}"
    GET_BEATMAPSET_PATH = "api/s/{}"
    DL_BEATMAP_PATH = "d/{}"
    SEMAPHORE = catboy_semaphore
    BEATMAP_CLASS = ChimuBeatmap
    BEATMAPSET_CLASS = ChimuBeatmapset
