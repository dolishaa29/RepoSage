import os
import smtplib
from email.message import EmailMessage


def is_configured():
    smtp_host = os.getenv("SMTP_HOST")
    sender = os.getenv("MAIL_FROM")
    return bool(smtp_host and sender)


def send_email(to: str, subject: str, text: str):
    sender = os.getenv("MAIL_FROM")
    message = EmailMessage()
    message["From"] = sender
    message["To"] = to
    message["Subject"] = subject
    message.set_content(text)

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as smtp_server:
        smtp_server.starttls()
        if smtp_user:
            smtp_server.login(smtp_user, os.getenv("SMTP_PASSWORD"))
        smtp_server.send_message(message)
