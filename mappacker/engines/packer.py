import os
import zipfile
from typing import List, Union, AsyncGenerator

from mappacker.models.job import Job


class BeatmapPacker:
    def __init__(self, job: Job):
        self.job = job

    async def run(self, filepaths: AsyncGenerator[str, None], job_id: Union[int, str]):
        zipfile_path = f"serve/{job_id}.zip"
        with open(zipfile_path, 'wb+') as temp_file:
            with zipfile.ZipFile(temp_file, mode='w', compression=zipfile.ZIP_DEFLATED) as temp_zip:
                async for fpath in filepaths:
                    if fpath is None:
                        continue
                    fdir, fname = os.path.split(fpath)
                    temp_zip.write(fpath, fname)
            return zipfile_path
