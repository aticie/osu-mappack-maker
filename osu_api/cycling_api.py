from typing import Union

from osu_api import AkatsukiAPI, ChimuAPI, DirectAPI, NerinyanAPI, GatariAPI, RippleAPI, CatboyAPI, OsuAPI


class CyclingAPI:
    def __init__(self):
        self.apis = [OsuAPI(), DirectAPI(), ChimuAPI(), NerinyanAPI(), AkatsukiAPI(), GatariAPI(), RippleAPI(), CatboyAPI()]

    async def get_beatmap(self, beatmap_id: Union[str, int]):
        for api in self.apis:
            if api.SEMAPHORE.locked():
                continue
            try:
                return await api.get_beatmap(beatmap_id=beatmap_id)
            except:
                continue

        raise Exception(f"Getting beatmap info for beatmap id {beatmap_id} failed.")

    async def download_beatmapset(self, beatmap):
        for api in self.apis:
            if api.SEMAPHORE.locked():
                continue
            try:
                return await api.download_beatmapset(beatmap=beatmap)
            except:
                continue

        raise Exception(f"Downloading beatmapset id {beatmap.beatmapset_id} failed.")
