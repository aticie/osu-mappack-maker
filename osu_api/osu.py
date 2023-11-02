import asyncio
import json
import logging
import os
from typing import Union
from urllib.parse import urljoin

import aiohttp
from aiohttp import ClientError

from osu_api.base_api import BaseAPI
from osu_models.chimu import ChimuBeatmapset
from osu_models.nerinyan import NerinyanBeatmap, NerinyanBeatmapset

osu_semaphore = asyncio.Semaphore(2)
logger = logging.getLogger(__name__)


class OsuAPI(BaseAPI):
    BEATMAP_CLASS = NerinyanBeatmap
    BEATMAPSET_CLASS = NerinyanBeatmapset
    BASE_URL = "https://osu.ppy.sh/"
    GET_BEATMAP_PATH = "api/v2/beatmaps/{}"
    GET_BEATMAPSET_PATH = "api/v2/beatmapsets/{}"
    DL_BEATMAP_PATH = "beatmapsets/{}/download"
    SEMAPHORE = osu_semaphore
    DL_BEATMAP_HEADERS = {"Cookie": f"osu_session={os.getenv('OSU_SESSION')}"}

    async def authorize(self):
        token_url = urljoin(self.BASE_URL, "oauth/token")
        params = {
            "client_id": os.getenv("OSU_CLIENT_ID"),
            "client_secret": os.getenv("OSU_CLIENT_SECRET"),
            "grant_type": "client_credentials",
            "scope": "public"
        }
        async with aiohttp.ClientSession() as sess:
            async with sess.post(token_url, json=params) as r:
                try:
                    resp = await r.json()
                except json.JSONDecodeError as e:
                    logger.error(e)

        access_token = resp["access_token"]
        self.API_AUTH_HEADERS = {
            "Authorization": f"Bearer {access_token}"
        }
        return access_token

    async def download_beatmapset(self, beatmapset: Union[NerinyanBeatmapset, ChimuBeatmapset], job_id: int):
        beatmapset_id = beatmapset.beatmapset_id
        self.DL_BEATMAP_HEADERS["Referer"] = f"https://osu.ppy.sh/beatmapsets/{beatmapset_id}"
        try:
            return await super(OsuAPI, self).download_beatmapset(beatmapset, job_id=job_id)
        except ClientError as e:
            r = e.args
            new_cookie = r.headers["set-cookie"]
            self.DL_BEATMAP_HEADERS["Cookie"] = new_cookie
            return await super(OsuAPI, self).download_beatmapset(beatmapset, job_id=job_id)
