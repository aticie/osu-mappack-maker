import asyncio
import logging
from async_lru import alru_cache
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import aiofiles
import aiohttp
from aiohttp.client_exceptions import ContentTypeError
from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

logger = logging.getLogger()
logger.setLevel("DEBUG")

app = FastAPI(title="main app")
api_app = FastAPI(title="api app")

semaphore = asyncio.Semaphore(5)


async def fetch_beatmapset_id_direct(beatmap_id):
    beatmap_url = f"https://osu.direct/api/v2/b/{beatmap_id}"
    print(f"Getting beatmap info: {beatmap_url}")
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url=beatmap_url) as r:
            resp = await r.json(encoding="utf-8")

        return resp["beatmapset_id"]

@alru_cache
async def fetch_beatmapset_id(beatmap_id: str):
    print(f"Fetch beatmapset id is called.")
    async with semaphore:
        beatmap_url = f"https://api.chimu.moe/v1/map/{beatmap_id}"
        print(f"Getting beatmap data: {beatmap_url}")
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url=beatmap_url) as r:
                try:
                    resp = await r.json(encoding="utf-8")
                    beatmapset_id = resp["ParentSetId"]
                except ContentTypeError as e:
                    return await fetch_beatmapset_id_direct(beatmap_id)
                except KeyError:
                    beatmapset_id = await fetch_beatmapset_id_direct(beatmap_id)
                await asyncio.sleep(1)
            return beatmapset_id


async def download_beatmap_nerinyan(beatmapset_id):
    download_url = f"https://api.nerinyan.moe/d/{beatmapset_id}"

    print(f"Downloading from nerinyan: {download_url}")
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url=download_url) as r:
            resp = await r.read()

        return resp


async def download_beatmap(beatmapset_id: int, save_folder: Path):
    beatmapset_filename = save_folder / f"{beatmapset_id}.osz"
    if beatmapset_filename.exists():
        print(f"{beatmapset_filename} exists, reading...")
        async with aiofiles.open(str(beatmapset_filename), "rb") as f:
            return await f.read(), beatmapset_id

    else:

        async with semaphore:
            download_url = f"https://api.chimu.moe/v1/download/{beatmapset_id}"
            print(f"Downloading: {download_url}")

            async with aiohttp.ClientSession() as sess:
                async with sess.get(url=download_url) as r2:
                    try:
                        if r2.status == 200:
                            beatmapset = await r2.read()
                        else:
                            print(f"Status code for download response was: {r2.status}")
                            beatmapset = await download_beatmap_nerinyan(beatmapset_id)
                    except ContentTypeError as e:
                        beatmapset = await download_beatmap_nerinyan(beatmapset_id)

                await asyncio.sleep(1)

                print(f"Saving: {beatmapset_filename}")
                async with aiofiles.open(str(beatmapset_filename), "wb") as f:
                    await f.write(beatmapset)

            return beatmapset, beatmapset_id


@api_app.get("/make_pool")
async def make_pool(beatmaps: str):
    save_folder = Path("beatmaps")
    save_folder.mkdir(exist_ok=True)

    fetch_tasks = []
    beatmaps_list = beatmaps.split(" ")
    beatmaps_list = list(filter(lambda x: (x != ''), beatmaps_list))
    if len(beatmaps_list) > 30:
        raise HTTPException(403, "Beatmap ids shouldn't be more than 30.")
    for beatmap in beatmaps_list:
        task = asyncio.create_task(fetch_beatmapset_id(beatmap_id=beatmap))
        fetch_tasks.append(task)

    download_tasks = []
    beatmapset_ids = {}
    for task in asyncio.as_completed(fetch_tasks):
        beatmapset_id = await task
        dl_task = asyncio.create_task(download_beatmap(beatmapset_id, save_folder=save_folder))
        beatmapset_ids[dl_task.get_coro()] = beatmapset_id
        download_tasks.append(dl_task)

    lock = asyncio.Lock()
    with ZipFile('beatmaps.zip', 'w', compression=ZIP_DEFLATED) as handle:
        for task in asyncio.as_completed(download_tasks):
            beatmapset_contents, beatmapset_id = await task
            async with lock:
                handle.writestr(f"{beatmapset_id}.osz", beatmapset_contents)

            print(f'.added f"{beatmapset_id}.osz"')

    return FileResponse("beatmaps.zip")


app.mount("/api", api_app)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
