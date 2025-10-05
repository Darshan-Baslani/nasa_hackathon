import os
from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "nasa")
BULK_COLLECTION = os.getenv("MONGO_BULK_COLLECTION", "nasa_bulk")
NEWSLETTER_COLLECTION = os.getenv("MONGO_NEWSLETTER_COLLECTION", "newsletter")

_client: Optional[AsyncIOMotorClient] = None


def _get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URI, server_api=ServerApi("1"))
    return _client


def get_database():
    return _get_client()[DB_NAME]


def get_collection(name: str = BULK_COLLECTION):
    return get_database()[name]


async def insert_aqi(aqi: list[dict]):
    """Replace the nasa_bulk collection contents with fresh AQI data."""
    collection = get_collection()
    await collection.delete_many({})
    if aqi:
        await collection.insert_many(aqi)


async def insert_newsletter_user(email: str, lat: float, lng: float):
    """Insert a new user into the newsletter collection."""
    collection = get_collection(NEWSLETTER_COLLECTION)
    await collection.insert_one({"email": email, "lat": lat, "lng": lng})
