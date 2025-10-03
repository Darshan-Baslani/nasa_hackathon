from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

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
collection = db['nasa_bulk']

async def insert_aqi(aqi: list[dict]):
    await collection.delete_many({})  # remove all old data
    await collection.insert_many(aqi)  # insert new data
