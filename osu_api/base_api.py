from typing import Union
from urllib.parse import urljoin

import aiofiles
import aiohttp
import pydantic


class BaseAPI:
    BASE_URL = None
    GET_BEATMAP_PATH = None
    DL_BEATMAP_PATH = None
    SEMAPHORE = None
    BEATMAP_CLASS = None

    async def get_beatmap(self, beatmap_id: Union[int, str]):
        url = urljoin(self.BASE_URL, self.GET_BEATMAP_PATH.format(beatmap_id))
        async with self.SEMAPHORE:
            print(f"Getting beatmap info: {url} from Direct.")
            async with aiohttp.ClientSession() as sess:
                async with sess.get(url=url) as r:
                    if r.status != 200:
                        print(url, r.status, await r.read())
                        raise aiohttp.ClientError()
                    resp = await r.json(encoding="utf-8")

                try:
                    return self.BEATMAP_CLASS(**resp)
                except pydantic.ValidationError as e:
                    print(f"Pydantic Validation error: {url}, {resp}")

    async def download_beatmapset(self, beatmap):
        async with self.SEMAPHORE:
            beatmapset_id = beatmap.beatmapset_id
            beatmapset_filename = f"{beatmapset_id}.osz"
            async with aiohttp.ClientSession() as sess:
                print(f"Downloading beatmapset for {beatmapset_id} with {self.__class__.__name__}.")
                url = urljoin(self.BASE_URL, self.DL_BEATMAP_PATH.format(beatmapset_id))
                async with sess.get(url) as r:
                    if r.status != 200:
                        print(url, r.status, await r.read())
                        raise aiohttp.ClientError()
                    response_bytes = await r.read()

                async with aiofiles.open(beatmapset_filename, "wb") as f:
                    await f.write(response_bytes)

            return beatmapset_filename
