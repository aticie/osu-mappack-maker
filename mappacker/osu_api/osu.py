import asyncio
import json
import logging
import os
from typing import Union
from urllib.parse import urljoin

from aiohttp import ClientError, ContentTypeError

from mappacker.osu_api.base_api import BaseAPI
from mappacker.osu_models.chimu import ChimuBeatmapset
from mappacker.osu_models.nerinyan import NerinyanBeatmap, NerinyanBeatmapset
from mappacker.utils.aiohttp import SingletonAiohttp

logger = logging.getLogger(__name__)


class OsuAPI(BaseAPI):
    BEATMAP_CLASS = NerinyanBeatmap
    BEATMAPSET_CLASS = NerinyanBeatmapset
    BASE_URL = "https://osu.ppy.sh/"
    GET_BEATMAP_PATH = "api/v2/beatmaps/{}"
    GET_BEATMAPSET_PATH = "api/v2/beatmapsets/{}"
    DL_BEATMAP_PATH = "beatmapsets/{}/download"
    SEMAPHORE = asyncio.Semaphore(2)
    AUTH_LOCK = asyncio.Lock()
    DL_BEATMAP_HEADERS = {"Cookie": f"osu_session={os.getenv('OSU_SESSION')}"}

    async def authorize(self):
        async with self.AUTH_LOCK:
            if self.rate_limited:
                logger.debug("Rate limited. Skipping authorization...")
                return
            if self.authorized:
                logger.debug("Already authorized, skipping...")
                return
            token_url = urljoin(self.BASE_URL, "oauth/token")
            params = {
                "client_id": os.getenv("OSU_CLIENT_ID"),
                "client_secret": os.getenv("OSU_CLIENT_SECRET"),
                "grant_type": "client_credentials",
                "scope": "public"
            }
            sess = SingletonAiohttp.get_aiohttp_client()
            async with sess.post(token_url, json=params) as r:
                try:
                    if r.status == 200:
                        resp = await r.json()
                    else:
                        resp = (await r.read()).decode()
                        logger.debug(f"We are rate-limited by osu!. Setting self.rate_limited=True. Response: {resp}")
                        self.rate_limited = True
                        return
                except (json.JSONDecodeError, ContentTypeError):
                    resp = (await r.read()).decode()
                    logger.exception(resp)
                    self.rate_limited = True
                    return

            access_token = resp["access_token"]
            self.API_AUTH_HEADERS = {
                "Authorization": f"Bearer {access_token}"
            }
            self.authorized = True
            logger.debug(f"osu! Authorization successful!")
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
