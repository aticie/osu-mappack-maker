from typing import Union

from osu_api import AkatsukiAPI, ChimuAPI, DirectAPI, NerinyanAPI, GatariAPI


class CyclingAPI:
    def __init__(self):
        self.apis = [DirectAPI(), ChimuAPI(), NerinyanAPI(), AkatsukiAPI(), GatariAPI()]

    async def get_beatmap(self, beatmap_id: Union[str, int]):
        for api in self.apis:
            try:
                beatmap = await api.get_beatmap(beatmap_id=beatmap_id)
                return beatmap
            except:
                continue

        raise Exception()

    async def download_beatmapset(self, beatmap):
        for api in self.apis:
            try:
                beatmapset_contents = await api.download_beatmapset(beatmap=beatmap)
                return beatmapset_contents
            except:
                continue

        raise Exception()
