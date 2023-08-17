import asyncio
import datetime
from typing import List, Union, Optional
from urllib.parse import urljoin

import aiohttp
from pydantic import BaseModel

from osu_api.base_api import BaseAPI

nerinyan_semaphore = asyncio.Semaphore(50)


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
    checksum: str
    max_combo: int


class HypeOrNominations(BaseModel):
    current: Optional[int] = None
    required: Optional[int] = None


class Availability(BaseModel):
    download_disabled: bool
    more_information: Optional[str] = None


class Description(BaseModel):
    description: Optional[str] = None


class GenreOrLanguage(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None


class NerinyanBeatmapset(BaseModel):
    artist: str
    artist_unicode: str
    creator: str
    favourite_count: int
    hype: HypeOrNominations
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
    has_favourited: bool
    beatmaps: List[NerinyanBeatmap]
    description: Optional[str] = None
    genre: GenreOrLanguage
    language: GenreOrLanguage
    ratings_string: Optional[str] = None


class NerinyanAPI(BaseAPI):
    BASE_URL = "https://api.nerinyan.moe/"
    GET_BEATMAP_PATH = "search"
    DL_BEATMAP_PATH = "d/{}"
    SEMAPHORE = nerinyan_semaphore
    BEATMAP_CLASS = NerinyanBeatmap

    async def get_beatmap(self, beatmap_id: Union[str, int]):
        async with nerinyan_semaphore:
            async with aiohttp.ClientSession() as sess:
                print(f"Getting beatmapset for {beatmap_id} from {self.__class__.__name__}.")
                params = {"q": beatmap_id,
                          "option": "mapId",
                          "s": "-2,-1,0,1,2,3,4"}
                url = urljoin(self.BASE_URL, self.GET_BEATMAP_PATH)
                async with sess.get(url, params=params) as r:
                    if r.status != 200:
                        raise aiohttp.ClientError()
                    response = await r.json()

                if len(response) == 0:
                    print(f"{beatmap_id} search returned 0 result.")
                    raise aiohttp.ClientError()
                print(f"Got the beatmapset for {beatmap_id}.")
                return self.BEATMAP_CLASS(**response[0])