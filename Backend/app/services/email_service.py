import os
import smtplib
from email.message import EmailMessage


def is_configured():
    return bool(os.getenv("SMTP_HOST") and os.getenv("MAIL_FROM"))


def send_email(to: str, subject: str, text: str):
    message = EmailMessage()
    message["From"] = os.getenv("MAIL_FROM")
    message["To"] = to
    message["Subject"] = subject
    message.set_content(text)

    with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT", "587")), timeout=30) as server:
        server.starttls()
        if os.getenv("SMTP_USER"):
            server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
        server.send_message(message)
