import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.core.logger import monitor_logger


def get_target_email() -> str:
    settings_file = "data/settings.json"
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("email_to", "")
        except Exception:
            pass
    return ""


def send_email(subject: str, body: str) -> None:
    target_email = get_target_email()
    if not all(
        [
            settings.smtp_server,
            settings.smtp_user,
            settings.smtp_password,
            target_email,
        ]
    ):
        monitor_logger.error("Missing SMTP configuration or target email, skipping email.")
        return

    msg = MIMEMultipart()
    msg["From"] = settings.smtp_user
    msg["To"] = target_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)
        server.quit()

        monitor_logger.info(f"Email sent successfully: {subject}")
    except smtplib.SMTPAuthenticationError as e:
        monitor_logger.error(
            f"SMTP Authentication Error: {e.smtp_code} - {e.smtp_error.decode('utf-8') if isinstance(e.smtp_error, bytes) else e.smtp_error}"
        )
    except Exception as e:
        monitor_logger.error(f"Failed to send email: {type(e).__name__} - {str(e)}")
