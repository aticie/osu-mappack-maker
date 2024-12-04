import asyncio
import gc
import hashlib
import json
import logging.config
import os
from asyncio import Queue
from typing import Dict, Union, Iterable, Any, AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket

from mappacker.engines import BeatmapDownloader, BeatmapGatherer, BeatmapPacker
from mappacker.models import Job
from mappacker.utils.aiohttp import SingletonAiohttp

logging.config.fileConfig('mappacker/logging.conf', disable_existing_loggers=False)

logger = logging.getLogger(__name__)

app = FastAPI(title="main app")
api_app = FastAPI(title="api app")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

job_queues: Dict[str, Queue] = {}

os.makedirs("serve", exist_ok=True)
gc.enable()


async def list_to_async_gen(list: Iterable[Any]) -> AsyncGenerator[Any, None]:
    for elem in list:
        yield elem


async def run(job: Job):
    job_id = job.job_hash
    logger.info(f"Starting task on job #{job_id}")
    gatherer = BeatmapGatherer(job)
    downloader = BeatmapDownloader(job)
    packer = BeatmapPacker(job)

    beatmap_gen = list_to_async_gen(job.beatmaps)
    beatmap_responses = gatherer.run(task_args=beatmap_gen)
    beatmap_files = downloader.run(task_args=beatmap_responses)
    zip_file = await packer.run(beatmap_files, job_id)
    job.result_path = zip_file
    job.completed = True
    job_queues.pop(job_id)
    gc.collect()


@api_app.websocket("/jobs/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: Union[int, str]):
    await websocket.accept()
    job_queue = job_queues[job_id]
    while True:
        message_json = await job_queue.get()
        logger.info(f"Websocket sending: {message_json}")
        await websocket.send_text(f"{message_json}")
        message = json.loads(message_json)
        if "completed" in message and message["completed"]:
            return


@api_app.get("/make_pool", response_class=PlainTextResponse)
async def make_pool(beatmaps: str):
    logger.info(f"Making a mappack for {beatmaps}...")

    beatmaps_list = beatmaps.split(" ")
    unique_beatmaps = set(map(str.strip, filter(lambda x: (x != ''), beatmaps_list)))

    if len(unique_beatmaps) > 30:
        raise HTTPException(400, "Beatmap ids can't be more than 30.")

    job_beatmaps = str(tuple(sorted(list(unique_beatmaps)))).encode()
    job_id = hashlib.md5(job_beatmaps).hexdigest()

    job_queue = Queue()
    job_queues[job_id] = job_queue

    job = Job(job_hash=job_id, beatmaps=unique_beatmaps, job_queue=job_queue)

    _ = asyncio.create_task(run(job=job))
    return job_id


async def on_start_up() -> None:
    logger.info(f"on_start_up calling SingletonAiohttp.get_aiohttp_client()")
    SingletonAiohttp.get_aiohttp_client()


async def on_shutdown() -> None:
    logger.info(f"on_shutdown calling SingletonAiohttp.close_aiohttp_client()")
    await SingletonAiohttp.close_aiohttp_client()


app.mount("/api", api_app)
app.mount("/serve", StaticFiles(directory="serve"), name="serve")
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=1, ws_max_size=1024 * 1024)
