import asyncio

from pydantic import BaseModel

from osu_api.base_api import BaseAPI

chimu_semaphore = asyncio.Semaphore(1)


class ChimuBeatmap(BaseModel):
    BeatmapId: int
    ParentSetId: int
    DiffName: str
    FileMD5: str
    Mode: int
    BPM: float
    AR: float
    OD: float
    CS: float
    HP: float
    TotalLength: int
    HitLength: int
    Playcount: int
    Passcount: int
    MaxCombo: int
    DifficultyRating: float
    OsuFile: str
    DownloadPath: str
    beatmapset_id: int

    def __init__(self, **data):
        data["beatmapset_id"] = data["ParentSetId"]
        super().__init__(**data)


class ChimuAPI(BaseAPI):
    BASE_URL = "https://api.chimu.moe/"
    GET_BEATMAP_PATH = "v1/map/{}"
    DL_BEATMAP_PATH = "v1/download/{}"
    SEMAPHORE = chimu_semaphore
    BEATMAP_CLASS = ChimuBeatmap
