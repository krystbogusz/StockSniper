from pydantic import BaseModel
from typing import Optional


class ProcessStatusResponse(BaseModel):
    is_running: bool
    pid: Optional[int] = None
    message: str


class ProcessActionResponse(BaseModel):
    success: bool
    message: str
