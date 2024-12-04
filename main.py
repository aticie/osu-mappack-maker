import asyncio
import gc
import hashlib
import logging.config
import os
from asyncio import Queue, Task
from typing import Dict, Union, Iterable, Any, AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket

from mappacker.engines import BeatmapDownloader, BeatmapGatherer, BeatmapPacker
from mappacker.models.job import Job, JobStatus
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

# Global job queue and status tracking
global_job_queue: Queue = Queue()
queued_job_ids: list[str] = []
jobs: Dict[str, Job] = {}
bg_worker_task: Task | None = None

os.makedirs("serve", exist_ok=True)
gc.enable()


async def list_to_async_gen(in_list: Iterable[Any]) -> AsyncGenerator[Any, None]:
    for elem in in_list:
        yield elem


async def run(job: Job):
    job_id = job.job_id
    job.job_status = JobStatus.IN_PROGRESS
    logger.info(f"Starting task on job #{job_id}")
    try:
        gatherer = BeatmapGatherer(job)
        downloader = BeatmapDownloader(job)
        packer = BeatmapPacker(job)

        beatmap_gen = list_to_async_gen(job.beatmaps)
        beatmap_responses = gatherer.run(task_args=beatmap_gen)
        beatmap_files = downloader.run(task_args=beatmap_responses)
        zip_file = await packer.run(beatmap_files, job_id)
        job.result_path = zip_file
        job.job_status = JobStatus.COMPLETED
    except Exception as e:
        logger.error(f"Error while processing job #{job_id}: {e}")
        job.job_status = JobStatus.FAILED
    finally:
        gc.collect()


async def job_worker():
    """Background worker to process jobs sequentially."""
    while True:
        job = await global_job_queue.get()
        jobs[job.job_id] = job
        await run(job)
        global_job_queue.task_done()
        queued_job_ids.remove(job.job_id)


@api_app.websocket("/jobs/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: Union[int, str]):
    await websocket.accept()
    job = jobs[job_id]
    if job.job_status is JobStatus.COMPLETED:
        job_dict = job.model_dump()
        await websocket.send_json(job_dict)

    while True:
        if job.job_status is JobStatus.QUEUED:
            queue_position = queued_job_ids.index(job.job_id) + 1
        else:
            queue_position = -1

        job_dict = job.model_dump()
        job_dict.update({"queue_position": queue_position})
        logger.info(f"Websocket sending: {job_dict}")
        await websocket.send_json(job_dict)

        if job_dict["job_status"] in [JobStatus.COMPLETED, JobStatus.FAILED]:
            break

        await asyncio.sleep(0.2)


@api_app.get("/make_pool", response_class=PlainTextResponse)
async def make_pool(beatmaps: str):
    logger.info(f"Making a mappack for {beatmaps}...")

    beatmaps_list = beatmaps.split(" ")
    unique_beatmaps = set(map(str.strip, filter(lambda x: (x != ''), beatmaps_list)))

    if len(unique_beatmaps) > 30:
        raise HTTPException(400, "Beatmap ids can't be more than 30.")

    job_beatmaps = str(tuple(sorted(list(unique_beatmaps)))).encode()
    job_id = hashlib.md5(job_beatmaps).hexdigest()

    if job_id in jobs:
        return job_id

    job = Job(job_id=job_id, beatmaps=unique_beatmaps)
    jobs[job_id] = job

    await global_job_queue.put(job)
    queued_job_ids.append(job_id)
    return job_id


@app.on_event("startup")
async def on_start_up() -> None:
    global bg_worker_task
    logger.info("Starting background worker.")
    SingletonAiohttp.get_aiohttp_client()
    bg_worker_task = asyncio.create_task(job_worker())


@app.on_event("shutdown")
async def on_shutdown() -> None:
    global bg_worker_task
    logger.info("Shutting down.")
    bg_worker_task.cancel()
    await SingletonAiohttp.close_aiohttp_client()


app.mount("/api", api_app)
app.mount("/serve", StaticFiles(directory="serve"), name="serve")
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=1, ws_max_size=1024 * 1024)
