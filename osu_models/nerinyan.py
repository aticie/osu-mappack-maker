import datetime
from typing import Optional, List, Union

from pydantic import BaseModel


class NerinyanBeatmap(BaseModel):
    difficulty_rating: float
    id: int
    mode: str
    status: str
    total_length: int
    user_id: int
    version: str
    accuracy: float
    ar: float
    beatmapset_id: int
    bpm: float
    convert: bool
    count_circles: int
    count_sliders: int
    count_spinners: int
    cs: float
    deleted_at: Optional[datetime.datetime] = None
    drain: float
    hit_length: int
    is_scoreable: bool
    last_updated: datetime.datetime
    mode_int: int
    passcount: int
    playcount: int
    ranked: int
    url: Optional[str] = None
    checksum: Optional[str] = None
    max_combo: Optional[int] = None


class HypeOrNominations(BaseModel):
    current: Optional[int] = None
    required: Optional[int] = None


class Availability(BaseModel):
    download_disabled: bool
    more_information: Optional[str] = None


class Description(BaseModel):
    description: Optional[str] = None


class GenreOrLanguage(BaseModel):
    id: Optional[Union[str,int]] = None
    name: Optional[Union[str,int]] = None


class NerinyanBeatmapset(BaseModel):
    artist: str
    artist_unicode: str
    creator: str
    favourite_count: int
    hype: Optional[HypeOrNominations] = None
    id: int
    nsfw: bool
    play_count: int
    preview_url: Optional[str] = None
    source: str
    status: str
    title: str
    title_unicode: str
    user_id: int
    video: bool
    availability: Availability
    bpm: float
    can_be_hyped: bool
    discussion_enabled: Optional[bool] = None
    discussion_locked: Optional[bool] = None
    is_scoreable: bool
    last_updated: datetime.datetime
    legacy_thread_url: str
    nominations_summary: HypeOrNominations
    ranked: int
    ranked_date: Optional[datetime.datetime] = None
    storyboard: bool
    submitted_date: datetime.datetime
    tags: str
    has_favourited: Optional[bool] = None
    beatmaps: List[NerinyanBeatmap]
    description: Optional[Description] = None
    genre: Optional[GenreOrLanguage] = None
    language: Optional[GenreOrLanguage] = None
    ratings_string: Optional[str] = None
    beatmapset_id: int

    def __init__(self, **data):
        data["beatmapset_id"] = data["id"]
        super().__init__(**data)
