import datetime
import logging
from typing import Optional, List, Union

from pydantic import BaseModel, Field, ConfigDict

logger = logging.getLogger(__name__)


class AliasableModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

class ChimuBeatmap(AliasableModel):
    BeatmapId: int = Field(..., validation_alias="BeatmapID")
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
        if "ParentSetID" in data and "ParentSetId" not in data:
            data["ParentSetId"] = data["ParentSetID"]
        if "ParentSetId" not in data:
            logger.error(f"ParentSetId is not in data: {data=}")
        data["beatmapset_id"] = data["ParentSetId"]
        super().__init__(**data)


class ChimuBeatmapset(AliasableModel):
    SetId: int
    ChildrenBeatmaps: List[ChimuBeatmap]
    RankedStatus: int
    ApprovedDate: Optional[Union[datetime.datetime | str]] = None
    LastUpdate: datetime.datetime
    LastChecked: datetime.datetime
    Artist: str
    Title: str
    Creator: str
    Source: str
    Tags: str
    HasVideo: bool
    Genre: Union[int, dict]
    Language: Union[int, dict]
    Favourites: int
    Disabled: Optional[bool] = None
    beatmapset_id: int
    artist: str
    title: str
    ranked: int

    def __init__(self, **data):
        if "SetID" in data and "SetId" not in data:
            data["SetId"] = data["SetID"]
        data["beatmapset_id"] = data["SetId"]
        data["artist"] = data["Artist"]
        data["title"] = data["Title"]
        data["ranked"] = data["RankedStatus"]
        super().__init__(**data)
