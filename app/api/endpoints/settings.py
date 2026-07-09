import os
import json
from fastapi import APIRouter
from app.schemas.settings import LoggingToggleRequest, EmailUpdateRequest, SettingsActionResponse, SettingsStateResponse

router = APIRouter()
SETTINGS_FILE = "data/settings.json"


def _read_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _write_settings(data: dict):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


@router.get("/", response_model=SettingsStateResponse)
async def get_settings():
    data = _read_settings()
    return SettingsStateResponse(
        logging_enabled=data.get("logging_enabled", True),
        email_to=data.get("email_to", "")
    )


@router.post("/logging", response_model=SettingsActionResponse)
async def toggle_logging(request: LoggingToggleRequest):
    settings_data = _read_settings()
    settings_data["logging_enabled"] = request.enabled
    _write_settings(settings_data)

    state_msg = "enabled" if request.enabled else "disabled"
    return SettingsActionResponse(
        success=True, message=f"Logging has been {state_msg}."
    )


@router.post("/email", response_model=SettingsActionResponse)
async def update_email(request: EmailUpdateRequest):
    settings_data = _read_settings()
    settings_data["email_to"] = request.email
    _write_settings(settings_data)

    return SettingsActionResponse(
        success=True, message="Target email has been updated."
    )
