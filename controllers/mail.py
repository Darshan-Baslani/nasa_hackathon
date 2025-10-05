from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
import os

from assets import mail_templates

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fm = FastMail(conf)

async def send_email_direct(email):
    message = MessageSchema(
        recipients=[email],
        subject=mail_templates.subject,
        body=mail_templates.body,
        subtype="html"
    )

    try:
        await fm.send_message(message)
        return {"message": "Email has been sent"}
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")