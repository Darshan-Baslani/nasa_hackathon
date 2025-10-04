from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

db_uri = os.getenv("MONGO_URI")

# client = MongoClient(db_uri, server_api=ServerApi('1'))

# db = client['nasa']
# collection = db['nasa_bulk']

# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)

# async def insert_aqi(aqi: list[dict]):
#     result = collection.insert_many(aqi) 
#     print(f"Inserted IDs: {result.inserted_ids}")


from motor.motor_asyncio import AsyncIOMotorClient

motor_client = AsyncIOMotorClient(db_uri, server_api=ServerApi('1'))
db = motor_client['nasa']
bulk_collection = db['nasa_bulk']
newsletter_collection = db['newsletter']


async def insert_aqi(aqi: list[dict]):
    await bulk_collection.delete_many({})  # remove all old data
    await bulk_collection.insert_many(aqi)  # insert new data

async def insert_newsletter_user(email: str, lat: float, lng: float):
    await newsletter_collection.insert_one({"email": email, "created_at": datetime.now(), "lat":lat, "lng":lng})

async def update_newsletter_user(email: str, lat: float, lng: float):
    await newsletter_collection.update_one({"email": email}, {"$set": {"lat": lat, "lng": lng}})

# async def get_newsletter_users():
#     return await newsletter_collection.find({}).to_list(length=None)

# async def delete_newsletter_user(email: str):
#     await newsletter_collection.delete_one({"email": email}) 