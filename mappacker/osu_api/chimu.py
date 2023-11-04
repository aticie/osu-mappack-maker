import asyncio

from mappacker.osu_api.base_api import BaseAPI
from mappacker.osu_models.chimu import ChimuBeatmap, ChimuBeatmapset


class ChimuAPI(BaseAPI):
    BASE_URL = "https://api.chimu.moe/"
    GET_BEATMAP_PATH = "v1/map/{}"
    GET_BEATMAPSET_PATH = "v1/set/{}"
    DL_BEATMAP_PATH = "v1/download/{}"
    SEMAPHORE = asyncio.Semaphore(3)
    BEATMAP_CLASS = ChimuBeatmap
    BEATMAPSET_CLASS = ChimuBeatmapset
