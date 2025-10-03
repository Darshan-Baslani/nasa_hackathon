from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from controllers.aqi import calculate_aqi, forecast_aqi
from controllers.aqi import bulk_aqi

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

@router.post("/bulk-aqi")
async def get_bulk_aqi(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(bulk_aqi)
        return {"message": f"Bulk AQI job started"}
    except Exception as e:
        raise HTTPException(500, f"Failed to start job: {str(e)}")