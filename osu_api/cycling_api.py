from typing import Union

import aiohttp

from osu_api.chimu import ChimuAPI
from osu_api.direct import DirectAPI
from osu_api.nerinyan import NerinyanAPI


class CyclingAPI:
    def __init__(self):
        self.apis = [DirectAPI(), ChimuAPI(), NerinyanAPI()]

    async def get_beatmap(self, beatmap_id: Union[str, int]):
        for api in self.apis:
            try:
                beatmap = await api.get_beatmap(beatmap_id=beatmap_id)
                return beatmap
            except aiohttp.ClientError as e:
                continue

        raise Exception()

    async def download_beatmapset(self, beatmapset_id: Union[str, int]):
        for api in self.apis:
            try:
                beatmapset_contents = await api.download_beatmapset(beatmapset_id=beatmapset_id)
                return beatmapset_contents
            except aiohttp.ClientError as e:
                continue

        raise Exception()
