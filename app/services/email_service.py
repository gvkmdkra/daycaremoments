"""Email Service - Send notifications via SMTP"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import Config


class EmailService:
    """Email service using SMTP"""

    def __init__(self):
        self.host = Config.EMAIL_HOST
        self.port = Config.EMAIL_PORT
        self.username = Config.EMAIL_HOST_USER
        self.password = Config.EMAIL_HOST_PASSWORD

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))

            with smtplib.SMTP_SSL(self.host, self.port) as server:
                server.login(self.username, self.password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False


def get_email_service():
    return EmailService()
