import logging
from typing import Union
from urllib.parse import urljoin

import aiofiles
import aiohttp
import pydantic

logger = logging.getLogger(__name__)


class BaseAPI:
    BASE_URL = None
    GET_BEATMAP_PATH = None
    DL_BEATMAP_PATH = None
    SEMAPHORE = None
    BEATMAP_CLASS = None
    GET_BEATMAP_HEADERS = {}
    DL_BEATMAP_HEADERS = {}

    def __init__(self):
        self.authorized = False

    async def get_beatmap(self, beatmap_id: Union[int, str]):
        if not self.authorized:
            await self.authorize()
        url = urljoin(self.BASE_URL, self.GET_BEATMAP_PATH.format(beatmap_id))
        async with self.SEMAPHORE:
            logger.info(f"Getting beatmap info: {url} from {self.__class__.__name__}.")
            async with aiohttp.ClientSession(headers=self.GET_BEATMAP_HEADERS) as sess:
                async with sess.get(url=url) as r:
                    if r.status != 200:
                        logger.error(url, r.status, await r.read())
                        raise aiohttp.ClientError()
                    resp = await r.json(encoding="utf-8")
                try:
                    return self.BEATMAP_CLASS(**resp)
                except pydantic.ValidationError as e:
                    logger.error(f"Pydantic Validation error: {url}, {resp}, {e}")

    async def download_beatmapset(self, beatmap) -> str:
        async with self.SEMAPHORE:
            beatmapset_id = beatmap.beatmapset_id
            beatmapset_filename = f"{beatmapset_id}.osz"
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

                async with aiofiles.open(beatmapset_filename, "wb") as f:
                    await f.write(response_bytes)

            return beatmapset_filename

    async def authorize(self):
        self.authorized = True
