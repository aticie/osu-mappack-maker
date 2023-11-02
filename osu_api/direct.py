from asyncio import Semaphore

from osu_models.nerinyan import NerinyanBeatmap, NerinyanBeatmapset
from osu_api.base_api import BaseAPI

direct_semaphore = Semaphore(5)


class DirectAPI(BaseAPI):
    BASE_URL = "https://osu.direct/api/"
    GET_BEATMAP_PATH = "v2/b/{}"
    GET_BEATMAPSET_PATH = "v2/s/{}"
    DL_BEATMAP_PATH = "d/{}"
    SEMAPHORE = direct_semaphore
    BEATMAP_CLASS = NerinyanBeatmap
    BEATMAPSET_CLASS = NerinyanBeatmapset
