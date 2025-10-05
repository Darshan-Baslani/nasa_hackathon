import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Query
from pydantic import BaseModel
import time
from typing import Optional
import uuid
import csv

from controllers.aqi import calculate_aqi, forecast_aqi, bulk_aqi
from db.mongo import get_collection


router = APIRouter()

_global_cache = {"ts": 0.0, "entries": None}
GLOBAL_PROJECTION = {
    "_id": 0,
    "data.city": 1,
    "data.iaqi": 1,
    "data.dominentpol": 1,
    "data.aqi": 1,
    "data.time.iso": 1,
    "data.attributions": 1,
}
CACHE_TTL_SECONDS = 60

class AQI(BaseModel):
    latitude: float
    longitude: float

@router.post("/aqi")
async def get_aqi(request: AQI):
    aqi = await calculate_aqi(request.latitude, request.longitude)
    return {"aqi": aqi}

@router.post("/forecast-aqi")
async def get_forecast_aqi(request: AQI):
    forecast = await forecast_aqi(request.latitude, request.longitude)
    return {"forecast": forecast}

@router.get("/bulk-aqi")
async def get_bulk_aqi_data(req: Request):
    req_id = str(uuid.uuid4())[:8]
    cities_file = (Path(__file__).resolve().parent / ".." / "data" / "cities.csv").resolve()
    if not cities_file.exists():
        raise HTTPException(500, "cities.csv not found")

    results = []
    with cities_file.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                lat = float(row.get("lat", 0))
                lng = float(row.get("lng", 0))
            except (TypeError, ValueError):
                continue

            city_result = {
                "city": row.get("city"),
                "id": row.get("id"),
                "lat": lat,
                "lng": lng,
                "country": row.get("country"),
            }

            try:
                city_result["aqi"] = await calculate_aqi(lat, lng)
            except Exception as exc:
                city_result["aqi_error"] = str(exc)

            results.append(city_result)

    return {"results": results}

@router.post("/bulk-aqi")
async def get_bulk_aqi(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(bulk_aqi)
        return {"message": f"Bulk AQI job started"}
    except Exception as e:
        raise HTTPException(500, f"Failed to start job: {str(e)}")

def schedule_bulk_aqi():
    print("cron job for bulk aqi started")
    asyncio.run(bulk_aqi())

@router.get("/global-aqi")
async def get_global_aqi(
    req: Request,
    limit: Optional[int] = Query(default=None, gt=0),
    country: Optional[str] = Query(default=None)
):
    req_id = str(uuid.uuid4())[:8]
    try:
        entries = await _get_global_entries()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Unable to fetch AQI data") from exc

    filtered = entries
    if country:
        token = country.lower()
        filtered = [entry for entry in entries if token in entry["search"]]

    payloads = [entry["payload"] for entry in filtered]

    if limit:
        payloads = payloads[:limit]

    return payloads




async def _refresh_global_cache():
    entries = []
    collection = get_collection()
    cursor = collection.find({}, GLOBAL_PROJECTION)

    async for doc in cursor:
        data = doc.get("data") or {}
        city = data.get("city") or {}
        geo = city.get("geo") or []
        if not isinstance(geo, (list, tuple)) or len(geo) < 2:
            continue
        try:
            lat = float(geo[0])
            lng = float(geo[1])
        except (TypeError, ValueError):
            continue

        iaqi = data.get("iaqi") or {}
        pollutants = {}
        for key, value in iaqi.items():
            if isinstance(value, dict):
                val = value.get("v")
            else:
                val = value
            if val is not None:
                pollutants[key] = val

        simplified = {
            "lat": lat,
            "lng": lng,
            "city": city.get("name"),
            "url": city.get("url"),
            "aqi": data.get("aqi"),
            "pollutants": pollutants,
            "dominant": data.get("dominentpol"),
            "time": (data.get("time") or {}).get("iso"),
        }

        attributions = data.get("attributions") or []
        search_parts = []
        if simplified["city"]:
            search_parts.append(str(simplified["city"]))
        if isinstance(attributions, list):
            for attribution in attributions:
                if isinstance(attribution, dict):
                    name = attribution.get("name")
                    if name:
                        search_parts.append(str(name))

        search_text = " ".join(part.lower() for part in search_parts if part)
        entries.append({"payload": simplified, "search": search_text})

    _global_cache["entries"] = entries
    _global_cache["ts"] = time.time()


async def _get_global_entries(force_refresh: bool = False):
    now = time.time()
    if force_refresh or not _global_cache["entries"] or (now - _global_cache["ts"]) > CACHE_TTL_SECONDS:
        await _refresh_global_cache()
    return _global_cache["entries"] or []