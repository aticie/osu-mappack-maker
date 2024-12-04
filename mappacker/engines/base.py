import asyncio
import logging
from itertools import cycle
from typing import Union, AsyncGenerator

from mappacker.models import Job
from mappacker.osu_api import *
from mappacker.osu_api.base_api import BaseAPI
from mappacker.osu_models.chimu import ChimuBeatmapset
from mappacker.osu_models.nerinyan import NerinyanBeatmapset

logger = logging.getLogger(__name__)


class BaseBeatmapEngine:
    def __init__(self, job: Job):
        self.apis = [OsuAPI(), DirectAPI(), NerinyanAPI(), AkatsukiAPI(), GatariAPI(), RippleAPI(),
                     CatboyAPI()]
        self.job = job

    async def run(self, task_args: AsyncGenerator[Union[str, int, NerinyanBeatmapset, ChimuBeatmapset], None]):
        tasks = []
        api_cycle = cycle(self.apis)
        async for task_arg in task_args:
            api = next(api_cycle)
            tasks.append(asyncio.create_task(self.gather_task(task_arg=task_arg, selected_api=api)))

        for completed_task in asyncio.as_completed(tasks):
            result = await completed_task
            yield result

    async def gather_task(self, task_arg: Union[str, int], selected_api: BaseAPI):
        raise NotImplementedError()
