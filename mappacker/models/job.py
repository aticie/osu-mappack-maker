import asyncio
from enum import Enum
from asyncio import Queue
from typing import Optional, Any

import pydantic
from pydantic import ConfigDict, Field, model_validator


class JobStatus(str, Enum):
    QUEUED = "Queued"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


class Job(pydantic.BaseModel, validate_assignment=True):
    model_config = ConfigDict(arbitrary_types_allowed=True, use_enum_values=True)

    job_id: str
    beatmaps: list[str] = Field(exclude=True)
    num_beatmaps: int = 0
    gathered: int = 0
    downloaded: int = 0
    result_path: Optional[str] = None
    errors: Optional[str] = None
    job_status: JobStatus = JobStatus.QUEUED
    job_events_queue: Queue = Field(Queue(), exclude=True)

    def model_post_init(self, __context: Any) -> None:
        self.num_beatmaps = len(self.beatmaps)

    @model_validator(mode="after")
    def post_progress(self):
        coro = self.job_events_queue.put(self.model_dump())
        asyncio.gather(coro)
        return self
