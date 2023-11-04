import asyncio
from asyncio import Queue
from typing import Optional

import pydantic
from pydantic import model_validator, Field, ConfigDict


class Job(pydantic.BaseModel, validate_assignment=True):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    job_hash: str
    beatmaps: int
    gathered: int = 0
    downloaded: int = 0
    completed: bool = False
    result_path: Optional[str] = None
    errors: Optional[str] = None
    job_queue: Queue = Field(exclude=True)

    @model_validator(mode="after")
    def post_progress(self):
        coro = self.job_queue.put(self.model_dump_json())
        asyncio.gather(coro)
        return self
