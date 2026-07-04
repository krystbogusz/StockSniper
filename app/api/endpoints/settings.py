import os
import json
from fastapi import APIRouter
from app.schemas.settings import LoggingToggleRequest, SettingsActionResponse

router = APIRouter()
SETTINGS_FILE = "data/settings.json"

@router.post("/logging", response_model=SettingsActionResponse)
async def toggle_logging(request: LoggingToggleRequest):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    
    settings_data = {}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings_data = json.load(f)
        except Exception:
            pass
            
    settings_data["logging_enabled"] = request.enabled
    
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings_data, f, indent=4)
        
    state_msg = "enabled" if request.enabled else "disabled"
    return SettingsActionResponse(success=True, message=f"Logging has been {state_msg}.")
