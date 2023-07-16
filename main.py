import asyncio
import logging
import uuid
from pathlib import Path

import aiofiles
from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
from zipstream import AioZipStream

from osu_api.cycling_api import CyclingAPI

logger = logging.getLogger()
logger.setLevel("DEBUG")

app = FastAPI(title="main app")
api_app = FastAPI(title="api app")
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

semaphore = asyncio.Semaphore(5)


@api_app.get("/make_pool")
async def make_pool(beatmaps: str):
    print(f"Making a mappack for {beatmaps}...")
    save_folder = Path("beatmaps")
    save_folder.mkdir(exist_ok=True)

    mappack_uuid = uuid.uuid4().hex
    mappack_filename = f"{mappack_uuid}.zip"

    fetch_tasks = []
    beatmaps_list = beatmaps.split(" ")
    beatmaps_list = list(filter(lambda x: (x != ''), beatmaps_list))

    if len(beatmaps_list) > 30:
        raise HTTPException(403, "Beatmap ids shouldn't be more than 30.")

    cycling_api = CyclingAPI()
    for beatmap in beatmaps_list:
        task = asyncio.create_task(cycling_api.get_beatmap(beatmap_id=beatmap))
        fetch_tasks.append(task)

    download_tasks = []

    for fetch_task in asyncio.as_completed(fetch_tasks):
        beatmap = await fetch_task
        beatmapset_id = beatmap.beatmapset_id
        dl_task = asyncio.create_task(cycling_api.download_beatmapset(beatmapset_id=beatmapset_id))
        download_tasks.append(dl_task)

    files = []
    for download_task in asyncio.as_completed(download_tasks):
        beatmapset_filename = await download_task
        files.append({"file": beatmapset_filename, "name": beatmapset_filename})

    aiozip = AioZipStream(files, chunksize=32768)
    async with aiofiles.open(mappack_filename, mode='wb') as z:
        async for chunk in aiozip.stream():
            await z.write(chunk)

    return FileResponse(mappack_filename, media_type="application/zip")


app.mount("/api", api_app)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
