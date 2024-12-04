import logging
from typing import Union

from mappacker.engines.base import BaseBeatmapEngine
from mappacker.osu_api import *
from mappacker.osu_api.base_api import BaseAPI
from mappacker.osu_models.chimu import ChimuBeatmapset
from mappacker.osu_models.nerinyan import NerinyanBeatmapset

logger = logging.getLogger(__name__)


class BeatmapGatherer(BaseBeatmapEngine):
    """Gathers beatmap information from beatmap ids."""

    async def gather_task(self, task_arg: Union[str, int], selected_api: BaseAPI) -> Union[
        ChimuBeatmapset, NerinyanBeatmapset]:
        remaining_apis = list(set(self.apis).difference({selected_api}))
        for api in [selected_api, *remaining_apis]:
            async with api.SEMAPHORE:
                try:
                    beatmap = await api.get_beatmap(beatmap_id=task_arg)
                    if not beatmap:
                        continue
                    if isinstance(api, NerinyanAPI):
                        beatmapset = beatmap
                    else:
                        beatmapset = await api.get_beatmapset(beatmapset_id=beatmap.beatmapset_id)
                    if not beatmapset:
                        continue
                    self.job.gathered += 1
                    return beatmapset
                except:
                    logger.exception(
                        f"Beatmap details could not be retrieved from {api.__class__.__name__}, trying next one.")
                    continue

        logger.error(f"Beatmap ID: {task_arg} was not found.")
        self.job.errors = f"Beatmap ID: {task_arg} was not found."
        self.job.errors = None
