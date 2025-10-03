import httpx
import json
from dotenv import load_dotenv
import os
import asyncio

from utils.preprocess import get_full_aqi, get_cities
from db import mongo

load_dotenv()

WAQI_API_KEY = os.getenv("WAQI_API_KEY")

async def calculate_aqi(latitude: float, longitude: float):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://api.waqi.info/feed/geo:{latitude};{longitude}/?token={WAQI_API_KEY}"
        )
    try:
        data = response.json()
    except Exception:
        raise ValueError(f"Non-JSON response: {response.text[:200]}")

    if isinstance(data['data'], str):
        print(data['data'])
        data['data'] = json.loads(data['data'])
    if isinstance(data['data']['aqi'], str):
        data['data']['aqi'] = json.loads(data['data']['aqi'])

    aqi = data["data"]["aqi"]
    return aqi


async def forecast_aqi(latitude: float, longitude: float):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://api.waqi.info/feed/geo:{latitude};{longitude}/?token={WAQI_API_KEY}"
        )
    try:
        data = response.json()
    except Exception:
        raise ValueError(f"Non-JSON response: {response.text[:200]}")

    if isinstance(data['data'], str):
        print(data['data'])
        data['data'] = json.loads(data['data'])
    if isinstance(data['data']['forecast'], str):
        data['data']['forecast'] = json.loads(data['data']['aqi'])

    aqi = data["data"]["forecast"]
    return aqi

async def bulk_aqi():
    cities: list[dict] = await get_cities()
    results = []
    async with httpx.AsyncClient() as client:
        for city in cities:
            results.append(get_full_aqi(client, city['lat'], city['lng']))
        results = await asyncio.gather(*results)
    await mongo.insert_aqi(results)
    print(results[0])

