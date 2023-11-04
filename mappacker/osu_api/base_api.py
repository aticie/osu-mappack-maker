import logging
import os
from threading import Lock
from typing import Union
from urllib.parse import urljoin

import aiofiles
import aiohttp
import pydantic

from mappacker.osu_models.chimu import ChimuBeatmapset
from mappacker.osu_models.nerinyan import NerinyanBeatmapset
from mappacker.utils.aiohttp import SingletonAiohttp

logger = logging.getLogger(__name__)


class SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class BaseAPI(metaclass=SingletonMeta):
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
        self.rate_limited = False

    async def get_endpoint(self, url: str):
        if self.rate_limited:
            return
        if not self.authorized:
            await self.authorize()
        logger.info(f"Getting beatmap info: {url} from {self.__class__.__name__}.")
        client = SingletonAiohttp.get_aiohttp_client()
        try:
            async with client.get(url=url, headers=self.API_AUTH_HEADERS, timeout=10) as r:
                if r.status != 200:
                    response_body = await r.read()
                    logger.error(f"Request to {url} failed due to status code:{r.status}\n{response_body.decode()}")
                    return
                resp = await r.json(encoding="utf-8")
                logger.debug(f"Response received by {self.__class__.__name__} for {url}: {resp}")
        except Exception:
            logger.exception(f"An error occured when getting the beatmap.")
            return

        return resp

    async def get_beatmap(self, beatmap_id: Union[int, str]):
        url = urljoin(self.BASE_URL, self.GET_BEATMAP_PATH.format(beatmap_id))
        resp = await self.get_endpoint(url)
        if not resp:
            return
        try:
            return self.BEATMAP_CLASS(**resp)
        except pydantic.ValidationError as e:
            logger.error(f"Pydantic Validation error: {url}, {resp}, {e}")

    async def get_beatmapset(self, beatmapset_id: Union[int, str]):
        if not beatmapset_id:
            return
        url = urljoin(self.BASE_URL, self.GET_BEATMAPSET_PATH.format(beatmapset_id))
        resp = await self.get_endpoint(url)
        if not resp:
            return
        try:
            return self.BEATMAPSET_CLASS(**resp)
        except pydantic.ValidationError as e:
            logger.error(f"Pydantic Validation error: {url}, {resp}, {e}")

    async def download_beatmapset(self, beatmapset: Union[NerinyanBeatmapset, ChimuBeatmapset],
                                  job_id: Union[int, str]) -> str:
        beatmapset_id = beatmapset.beatmapset_id
        beatmapset_filename = f"{beatmapset_id} {beatmapset.artist} - {beatmapset.title}.osz"
        save_folder = os.path.join("serve", str(job_id))
        os.makedirs(save_folder, exist_ok=True)
        beatmapset_filepath = os.path.join(save_folder, beatmapset_filename)

        logger.info(f"Downloading beatmapset for {beatmapset_id} with {self.__class__.__name__}.")
        url = urljoin(self.BASE_URL, self.DL_BEATMAP_PATH.format(beatmapset_id))
        client = SingletonAiohttp.get_aiohttp_client()
        try:
            async with client.get(url=url, headers=self.DL_BEATMAP_HEADERS, timeout=20) as r:
                if r.status != 200:
                    logger.error(f"{url}, {r.status}, {await r.read()}")
                    raise aiohttp.ClientError()
                elif ("Content-Type" in r.headers) and \
                        (r.headers["Content-Type"] != "application/octet-stream") == \
                        (r.headers["Content-Type"] != "application/x-osu-beatmap-archive"):
                    resp = (await r.read()).decode()
                    logger.error(
                        f"Header mismatch. Requested url: {url} with {self.DL_BEATMAP_HEADERS=}\n"
                        f"Received headers: {r.headers}.\n"
                        f"Content Type mismatch: {r.headers['Content-Type']}\n"
                        f"Response: {resp}")
                    raise aiohttp.ClientError(r)
                response_bytes = await r.read()
        except Exception:
            logger.exception(f"An error occured when downloading the beatmapset {beatmapset_id} from {url}.")
            raise aiohttp.ClientError()

        async with aiofiles.open(beatmapset_filepath, "wb") as f:
            await f.write(response_bytes)

        logger.info(
            f"Beatmapset {beatmapset_id} successfully downloaded from {self.__class__.__name__}. {beatmapset_filepath=}")
        return beatmapset_filepath

    async def authorize(self):
        self.authorized = True
