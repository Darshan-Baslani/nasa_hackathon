import httpx
import json
from dotenv import load_dotenv
import os

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