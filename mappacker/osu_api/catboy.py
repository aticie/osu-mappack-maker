import asyncio

from mappacker.osu_api.base_api import BaseAPI
from mappacker.osu_models.chimu import ChimuBeatmap, ChimuBeatmapset


class CatboyAPI(BaseAPI):
    BASE_URL = "https://catboy.best/"
    GET_BEATMAP_PATH = "api/b/{}"
    GET_BEATMAPSET_PATH = "api/s/{}"
    DL_BEATMAP_PATH = "d/{}"
    SEMAPHORE = asyncio.Semaphore(1)
    BEATMAP_CLASS = ChimuBeatmap
    BEATMAPSET_CLASS = ChimuBeatmapset
