from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = None

async def connect_to_mongo():
    global client
    if client is None:
        client = AsyncIOMotorClient(MONGO_URI)
        await client.server_info()  # Ensures the connection is valid

async def close_mongo_connection():
    global client
    if client:
        client.close()

async def get_database():
    global client
    if client is None:
        raise Exception("MongoDB client is not initialized. Call 'connect_to_mongo' first.")
    return client.fido_database
