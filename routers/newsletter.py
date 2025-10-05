from fastapi import BackgroundTasks, HTTPException, APIRouter
from pydantic import BaseModel, EmailStr
from typing import List
from dotenv import load_dotenv

from controllers.mail import send_email_direct
from db import mongo


class Newsletter(BaseModel):
    email: EmailStr
    lat: float
    lng: float

router = APIRouter()

@router.post("/add-user-to-newsletter")
async def newsletter(request: Newsletter, background_tasks: BackgroundTasks):
    background_tasks.add_task(mongo.insert_newsletter_user, request.email, request.lat, request.lng)
    background_tasks.add_task(send_email_direct, request.email)
    return {"message": "Newsletter user added"}