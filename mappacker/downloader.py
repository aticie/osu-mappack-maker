import asyncio
from typing import AsyncGenerator, Union

from models import Job
from osu_api import *
from osu_models.chimu import ChimuBeatmapset
from osu_models.nerinyan import NerinyanBeatmapset


class BeatmapDownloader:
    def __init__(self, job: Job):
        self.apis = [OsuAPI(), DirectAPI(), ChimuAPI(), NerinyanAPI(), AkatsukiAPI(), GatariAPI(), RippleAPI(),
                     CatboyAPI()]
        self.job = job

    async def run(self, beatmap_responses: AsyncGenerator[Union[NerinyanBeatmapset, ChimuBeatmapset], None],
                  job_id: Union[int, str]):
        tasks = []
        async for beatmap in beatmap_responses:
            tasks.append(asyncio.create_task(self.download_beatmap(beatmap, job_id)))

        beatmap_files = []
        for task in asyncio.as_completed(tasks):
            beatmap_files.append(await task)

        return beatmap_files

    async def download_beatmap(self, beatmapset: Union[NerinyanBeatmapset, ChimuBeatmapset], job_id: Union[int, str]):
        if beatmapset is None:
            return
        for api in self.apis:
            if api.SEMAPHORE.locked():
                continue
            try:
                filepath = await api.download_beatmapset(beatmapset=beatmapset, job_id=job_id)
                self.job.downloaded += 1
                return filepath
            except:
                continue

        self.job.errors = f"Beatmapset {beatmapset.beatmapset_id} could not be downloaded from any mirrors."
        self.job.errors = None