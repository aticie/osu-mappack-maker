import datetime
from typing import Optional, List

from pydantic import BaseModel


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
    OsuFile: Optional[str] = None
    DownloadPath: Optional[str] = None
    beatmapset_id: int

    def __init__(self, **data):
        data["beatmapset_id"] = data["ParentSetId"]
        super().__init__(**data)


class ChimuBeatmapset(BaseModel):
    SetId: int
    ChildrenBeatmaps: List[ChimuBeatmap]
    RankedStatus: int
    ApprovedDate: datetime.datetime
    LastUpdate: datetime.datetime
    LastChecked: datetime.datetime
    Artist: str
    Title: str
    Creator: str
    Source: str
    Tags: str
    HasVideo: bool
    Genre: int
    Language: int
    Favourites: int
    Disabled: bool
    beatmapset_id: int
    artist: str
    title: str
    ranked: int

    def __init__(self, **data):
        data["beatmapset_id"] = data["SetId"]
        data["artist"] = data["Artist"]
        data["title"] = data["Title"]
        data["ranked"] = data["RankedStatus"]
        super().__init__(**data)
