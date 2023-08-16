import logging
import asyncio
from collections import namedtuple

from osu_api.osu import OsuAPI

if __name__ == '__main__':
    logger = logging.getLogger()
    api = OsuAPI()
    Beatmap = namedtuple("Beatmap", ["beatmapset_id"])
    beatmap = Beatmap(beatmapset_id=1944151)
    beatmapset_contents = asyncio.run(api.download_beatmapset(beatmap=beatmap))
    print(beatmapset_contents)