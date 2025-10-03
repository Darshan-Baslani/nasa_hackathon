import pandas as pd
import httpx
import json
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
WAQI_API_KEY = os.getenv("WAQI_API_KEY")
CONCURRENCY = 100
sem = asyncio.Semaphore(CONCURRENCY)
API_URL = "http://api.waqi.info/feed/geo:{lat};{lon}/?token={key}"

# async def get_cities() -> dict:
#     df = pd.read_csv("data/cities.csv")
#     return df.to_dict(orient="records")

CITIES_CACHE = None

async def get_cities() -> list[dict]:
    global CITIES_CACHE
    if CITIES_CACHE is None:
        df = pd.read_csv("data/cities.csv")
        CITIES_CACHE = df.to_dict(orient="records")
    return CITIES_CACHE

async def get_full_aqi(client: httpx.AsyncClient, lat: float, lon: float):
    async with sem:
        try:
            url = API_URL.format(lat=lat, lon=lon, key=WAQI_API_KEY)
            r = await client.get(url, timeout=10.0)
            return r.json()
        except Exception as e:
            return {"lat": lat, "lon": lon, "error": str(e)}