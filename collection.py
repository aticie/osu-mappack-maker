import asyncio
from pathlib import Path
from typing import Dict

import aiofiles
from aiofiles.tempfile import SpooledTemporaryFile


class Collection:
    def __init__(self, name: str):
        self.name = name
        self.beatmaps = set()

    def add_bmap(self, beatmap_md5: str):
        self.beatmaps.add(beatmap_md5)

    async def write(self, fileh):
        await fileh.write(get_string(self.name))
        await fileh.write(len(self.beatmaps).to_bytes(length=4, byteorder='little'))
        for beatmap in self.beatmaps:
            await fileh.write(get_string(beatmap))


class CollectionDB:

    def __init__(self, file: SpooledTemporaryFile):
        self.version = 0
        self.nr_collections = 0
        self.collections = {}
        loop = asyncio.get_running_loop()
        self.task = loop.create_task(self.parse_collection(file))


    async def parse_collection(self, file):
        self.version = await read_int(file)
        self.nr_collections = await read_int(file)

        self.collections: Dict[str, Collection] = {}
        for col_no in range(self.nr_collections):
            collection_name = await parse_string(file)
            nr_beatmaps = await read_int(file)
            collection = Collection(collection_name)

            for i in range(nr_beatmaps):
                beatmap_md5 = await parse_string(file)
                collection.add_bmap(beatmap_md5)

            self.collections[collection.name] = collection

    def add_collection(self, collection: Collection):
        self.collections[collection.name] = collection
        self.nr_collections += 1

    async def save(self, save_path: Path):
        async with aiofiles.open(save_path, 'wb') as f:
            await f.write(self.version.to_bytes(length=4, byteorder='little'))
            await f.write(self.nr_collections.to_bytes(length=4, byteorder='little'))
            for collection in self.collections.values():
                await collection.write(f)


async def parse_string(fileobj):
    # Get next byte, this one indicates what the rest of the string is
    indicator = await fileobj.read(1)

    if ord(indicator) == 0:
        # The next two parts are not present.
        # log.log(5, "Read empty STRING")
        return ""
    elif ord(indicator) == 11:
        # The next two parts are present.
        # The first part is a ULEB128. Get that.
        uleb = await parse_uleb128(fileobj)
        # log.log(5, "Read {} as ULEB128".format(uleb))
        s_bytes = await fileobj.read(uleb)
        s = s_bytes.decode('utf-8')
        # log.log(5, "Read {} as STRING".format(s))
        return s


async def parse_uleb128(fileobj):
    """
    Get an Unsigned Little Endian Base 128 integer from the file object
    :param fileobj: The file object
    :type fileobj: FileIO[bytes]
    :return: The integer
    """

    result = 0
    shift = 0
    while True:
        byte = await fileobj.read(1)
        byte_int = byte[0]
        result |= (byte_int & 0x7F) << shift

        if ((byte_int & 0x80) >> 7) == 0:
            break

        shift += 7

    return result


def get_string(string):
    if not string:
        # If the string is empty, the string consists of just this byte
        return bytes([0x00])
    else:
        # Else, it starts with 0x0b
        result = bytes([0x0b])

        # Followed by the length of the string as an ULEB128
        encoded = string.encode('utf-8')
        result += get_uleb128(len(encoded))

        # Followed by the string in UTF-8
        result += encoded
        return result


def get_uleb128(integer):
    cont_loop = True
    result = b''

    while cont_loop:
        byte = integer & 0x7F
        integer >>= 7
        if integer != 0:
            byte |= 0x80
        result += bytes([byte])
        cont_loop = integer != 0

    return result


async def read_int(fileh):
    return int.from_bytes(await fileh.read(4), byteorder='little')
