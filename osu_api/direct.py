from asyncio import Semaphore
from pydantic import BaseModel

from osu_api.base_api import BaseAPI

direct_semaphore = Semaphore(5)


class DirectBeatmap(BaseModel):
    ParentSetID: int
    BeatmapID: int
    TotalLength: int
    HitLength: int
    DiffName: str
    FileMD5: str
    CS: float
    AR: float
    HP: float
    OD: float
    Mode: int
    BPM: float
    Playcount: int
    Passcount: int
    MaxCombo: int
    DifficultyRating: float
    beatmapset_id: int

    def __init__(self, **data):
        data["beatmapset_id"] = data["ParentSetID"]
        super().__init__(**data)


class DirectAPI(BaseAPI):
    BASE_URL = "https://osu.direct/api/"
    GET_BEATMAP_PATH = "b/{}"
    DL_BEATMAP_PATH = "d/{}"
    SEMAPHORE = direct_semaphore
    BEATMAP_CLASS = DirectBeatmap

