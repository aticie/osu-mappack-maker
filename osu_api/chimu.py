import asyncio

from osu_api.base_api import BaseAPI
from osu_models.chimu import ChimuBeatmap, ChimuBeatmapset

chimu_semaphore = asyncio.Semaphore(1)


class ChimuAPI(BaseAPI):
    BASE_URL = "https://api.chimu.moe/"
    GET_BEATMAP_PATH = "v1/map/{}"
    GET_BEATMAPSET_PATH = "v1/set/{}"
    DL_BEATMAP_PATH = "v1/download/{}"
    SEMAPHORE = chimu_semaphore
    BEATMAP_CLASS = ChimuBeatmap
    BEATMAPSET_CLASS = ChimuBeatmapset
