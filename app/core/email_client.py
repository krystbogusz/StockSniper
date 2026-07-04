import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_email(subject: str, body: str) -> None:
    if not all([settings.smtp_server, settings.smtp_user, settings.smtp_password, settings.email_to]):
        print("Missing SMTP configuration, skipping email.", flush=True)
        return

    msg = MIMEMultipart()
    msg['From'] = settings.smtp_user
    msg['To'] = settings.email_to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent: {subject}", flush=True)
    except Exception as e:
        print(f"Failed to send email: {e}", flush=True)
