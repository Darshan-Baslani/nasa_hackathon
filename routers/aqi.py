from fastapi import APIRouter
from pydantic import BaseModel
from controllers.aqi import calculate_aqi, forecast_aqi

router = APIRouter()

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