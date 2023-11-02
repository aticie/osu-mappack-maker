import asyncio
from typing import Union, Iterable

from models import Job
from osu_api import *
from osu_api.catboy import CatboyAPI
from osu_models.chimu import ChimuBeatmapset
from osu_models.nerinyan import NerinyanBeatmapset


class BeatmapGatherer:
    """Gathers beatmap information from beatmap ids."""

    def __init__(self, job: Job):
        self.apis = [OsuAPI(), DirectAPI(), ChimuAPI(), NerinyanAPI(), CatboyAPI()]
        self.job = job

    async def run(self, beatmap_ids: Iterable[Union[str, int]]):
        tasks = []
        for beatmap_id in beatmap_ids:
            tasks.append(asyncio.create_task(self.gather_beatmapset(beatmap_id=beatmap_id)))

        for i, completed_task in enumerate(asyncio.as_completed(tasks)):
            yield await completed_task

    async def gather_beatmapset(self, beatmap_id: Union[str, int]) -> Union[ChimuBeatmapset, NerinyanBeatmapset]:
        for api in self.apis:
            if api.SEMAPHORE.locked():
                continue
            try:
                beatmap = await api.get_beatmap(beatmap_id=beatmap_id)
                beatmapset = await api.get_beatmapset(beatmapset_id=beatmap.beatmapset_id)
                self.job.gathered += 1
                return beatmapset
            except:
                continue

        self.job.errors = f"Beatmap ID: {beatmap_id} was not found."
        self.job.errors = None