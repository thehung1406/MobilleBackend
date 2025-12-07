import smtplib
from email.message import EmailMessage
from app.core.config import settings

def send_mail(to: str, subject: str, html: str):
    msg = EmailMessage()
    msg["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(html, subtype="html")

    if settings.MAIL_SSL_TLS:
        with smtplib.SMTP_SSL(settings.MAIL_SERVER, settings.MAIL_PORT) as s:
            if settings.MAIL_USERNAME:
                s.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD or "")
            s.send_message(msg)
    else:
        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as s:
            if settings.MAIL_STARTTLS:
                s.starttls()
            if settings.MAIL_USERNAME:
                s.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD or "")
            s.send_message(msg)
