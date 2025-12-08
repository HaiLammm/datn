from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List, Dict, Any
from pydantic import EmailStr

from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=settings.TEMPLATE_FOLDER
)

fm = FastMail(conf)

async def send_email(
    recipients: List[EmailStr],
    subject: str,
    template_name: str,
    template_body: Dict[str, Any]
):
    """
    Sends an email using a template.
    """
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        template_body=template_body,
        subtype="html"
    )
    await fm.send_message(message, template_name=template_name)
