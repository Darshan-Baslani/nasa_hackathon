from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi import BackgroundTasks, HTTPException, APIRouter
from pydantic import BaseModel, EmailStr
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()

class EmailSchema(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=EmailStr(os.getenv("MAIL_FROM")),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fm = FastMail(conf)

router = APIRouter()

@router.post("/send-email/")
async def send_email(email: EmailSchema, background_tasks: BackgroundTasks):
    message = MessageSchema(
        subject=email.subject,
        recipients=email.to,
        body=email.body,
        subtype="html"
    )

    try:
        background_tasks.add_task(fm.send_message, message)
        return {"message": "Email has been scheduled to be sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")