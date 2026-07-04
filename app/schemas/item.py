from pydantic import BaseModel, HttpUrl
from typing import Dict

class ItemRequest(BaseModel):
    url: str

class ItemListResponse(BaseModel):
    items: Dict[str, str]

class ItemActionResponse(BaseModel):
    success: bool
    message: str
