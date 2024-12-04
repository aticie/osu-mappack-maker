import logging
from typing import Union

from mappacker.engines.base import BaseBeatmapEngine
from mappacker.osu_api.base_api import BaseAPI
from mappacker.osu_models.chimu import ChimuBeatmapset
from mappacker.osu_models.nerinyan import NerinyanBeatmapset

logger = logging.getLogger(__name__)


class BeatmapDownloader(BaseBeatmapEngine):
    async def gather_task(self, task_arg: Union[NerinyanBeatmapset, ChimuBeatmapset], selected_api: BaseAPI) -> str:
        remaining_apis = list(set(self.apis).difference({selected_api}))
        for api in [selected_api, *remaining_apis]:
            async with api.SEMAPHORE:
                try:
                    filepath = await api.download_beatmapset(beatmapset=task_arg, job_id=self.job.job_hash)
                    self.job.downloaded += 1
                    return filepath
                except:
                    logger.info(f"Beatmapset {task_arg} could not be downloaded from {api.__class__.__name__}, trying next one.")
                    continue
        logger.error(f"Beatmapset {task_arg.beatmapset_id} could not be downloaded from any mirrors.")
        self.job.errors = f"Beatmapset {task_arg.beatmapset_id} could not be downloaded from any mirrors."
        self.job.errors = None
