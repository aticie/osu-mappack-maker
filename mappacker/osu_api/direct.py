from asyncio import Semaphore

from mappacker.osu_api.base_api import BaseAPI
from mappacker.osu_models.nerinyan import NerinyanBeatmap, NerinyanBeatmapset


class DirectAPI(BaseAPI):
    BASE_URL = "https://osu.direct/api/"
    GET_BEATMAP_PATH = "v2/b/{}"
    GET_BEATMAPSET_PATH = "v2/s/{}"
    DL_BEATMAP_PATH = "d/{}"
    SEMAPHORE = Semaphore(5)
    BEATMAP_CLASS = NerinyanBeatmap
    BEATMAPSET_CLASS = NerinyanBeatmapset
