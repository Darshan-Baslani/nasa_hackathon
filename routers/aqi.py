from fastapi import APIRouter
from pydantic import BaseModel
from controllers.aqi import calculate_aqi

router = APIRouter()

class AQI(BaseModel):
    latitude: float
    longitude: float

@router.get("/aqi")
async def get_aqi(request: AQI):
    aqi = await calculate_aqi(request.latitude, request.longitude)
    return {"aqi": aqi}
