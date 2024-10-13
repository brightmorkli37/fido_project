from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = None

async def connect_to_mongo():
    global client
    client = AsyncIOMotorClient(MONGO_URI)
    await client.server_info()  # This will raise an exception if the connection fails

async def close_mongo_connection():
    global client
    if client:
        client.close()

async def get_database():
    db = client.fido_database
    return db