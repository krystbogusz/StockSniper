from pydantic import BaseModel


class LoggingToggleRequest(BaseModel):
    enabled: bool


class EmailUpdateRequest(BaseModel):
    email: str


class SettingsStateResponse(BaseModel):
    logging_enabled: bool
    email_to: str


class SettingsActionResponse(BaseModel):
    success: bool
    message: str
