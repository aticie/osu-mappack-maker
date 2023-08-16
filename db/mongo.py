import os

import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
database = client.MAPPACK_MAKER
collection = database.get_collection("Mappacks")