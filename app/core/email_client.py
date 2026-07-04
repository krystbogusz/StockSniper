import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.core.logger import monitor_logger


def send_email(subject: str, body: str) -> None:
    if not all(
        [
            settings.smtp_server,
            settings.smtp_user,
            settings.smtp_password,
            settings.email_to,
        ]
    ):
        monitor_logger.error("Missing SMTP configuration, skipping email.")
        return

    msg = MIMEMultipart()
    msg["From"] = settings.smtp_user
    msg["To"] = settings.email_to
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
