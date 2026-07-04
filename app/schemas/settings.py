from pydantic import BaseModel

class LoggingToggleRequest(BaseModel):
    enabled: bool

class SettingsActionResponse(BaseModel):
    success: bool
    message: str
