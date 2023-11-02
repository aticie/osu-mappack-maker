import logging
import os
from typing import Union
from urllib.parse import urljoin

import aiofiles
import aiohttp
import pydantic

from osu_models.chimu import ChimuBeatmapset
from osu_models.nerinyan import NerinyanBeatmapset

logger = logging.getLogger(__name__)


class BaseAPI:
    BASE_URL = None
    GET_BEATMAP_PATH = None
    GET_BEATMAPSET_PATH = None
    DL_BEATMAP_PATH = None
    SEMAPHORE = None
    BEATMAP_CLASS = None
    BEATMAPSET_CLASS = None
    API_AUTH_HEADERS = {}
    DL_BEATMAP_HEADERS = {}

    def __init__(self):
        self.authorized = False

    async def get_endpoint(self, url: str):
        if not self.authorized:
            await self.authorize()
        async with self.SEMAPHORE:
            logger.info(f"Getting beatmap info: {url} from {self.__class__.__name__}.")
            async with aiohttp.ClientSession(headers=self.API_AUTH_HEADERS) as sess:
                async with sess.get(url=url) as r:
                    if r.status != 200:
                        response_body = await r.read()
                        logger.error(url, r.status, response_body.decode())
                        raise aiohttp.ClientError()
                    resp = await r.json(encoding="utf-8")
            return resp

    async def get_beatmap(self, beatmap_id: Union[int, str]):
        url = urljoin(self.BASE_URL, self.GET_BEATMAP_PATH.format(beatmap_id))
        resp = await self.get_endpoint(url)
        try:
            return self.BEATMAP_CLASS(**resp)
        except pydantic.ValidationError as e:
            logger.error(f"Pydantic Validation error: {url}, {resp}, {e}")

    async def get_beatmapset(self, beatmapset_id: Union[int, str]):
        url = urljoin(self.BASE_URL, self.GET_BEATMAPSET_PATH.format(beatmapset_id))
        resp = await self.get_endpoint(url)
        try:
            return self.BEATMAPSET_CLASS(**resp)
        except pydantic.ValidationError as e:
            logger.error(f"Pydantic Validation error: {url}, {resp}, {e}")

    async def download_beatmapset(self, beatmapset: Union[NerinyanBeatmapset, ChimuBeatmapset], job_id: int) -> str:
        async with self.SEMAPHORE:
            beatmapset_id = beatmapset.beatmapset_id
            beatmapset_filename = f"{beatmapset_id} {beatmapset.artist} - {beatmapset.title}.osz"
            save_folder = os.path.join("serve", str(job_id))
            os.makedirs(save_folder, exist_ok=True)
            beatmapset_filepath = os.path.join(save_folder, beatmapset_filename)

            async with aiohttp.ClientSession(headers=self.DL_BEATMAP_HEADERS) as sess:
                logger.info(f"Downloading beatmapset for {beatmapset_id} with {self.__class__.__name__}.")
                url = urljoin(self.BASE_URL, self.DL_BEATMAP_PATH.format(beatmapset_id))
                async with sess.get(url) as r:
                    if r.status != 200:
                        logger.error(f"{url}, {r.status}, {await r.read()}")
                        raise aiohttp.ClientError()
                    elif (r.headers["Content-Type"] != "application/octet-stream") == \
                            (r.headers["Content-Type"] != "application/x-osu-beatmap-archive"):
                        logger.error(
                            f"Header mismatch. Requested url: {url}\n"
                            f"Received headers: {r.headers}.\n"
                            f"Content Type mismatch: {r.headers['Content-Type']}\n")
                        raise aiohttp.ClientError(r)
                    response_bytes = await r.read()

                async with aiofiles.open(beatmapset_filepath, "wb") as f:
                    await f.write(response_bytes)

            logger.info(f"Beatmap successfully downloaded from {self.__class__.__name__}.\n{beatmapset_filepath=}")
            return beatmapset_filepath

    async def authorize(self):
        self.authorized = True
