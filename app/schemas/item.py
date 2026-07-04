from pydantic import BaseModel, model_validator
from typing import Dict, List, Literal


def validate_interval(value: int, unit: str) -> int:
    multiplier = {"seconds": 1, "minutes": 60, "hours": 3600}[unit]
    seconds = value * multiplier
    if seconds < 30:
        raise ValueError("Interval must be at least 30 seconds.")
    return seconds


class ItemRequest(BaseModel):
    url: str
    size: str
    interval_value: int
    interval_unit: Literal["seconds", "minutes", "hours"]

    @model_validator(mode="after")
    def check_min_interval(self) -> "ItemRequest":
        validate_interval(self.interval_value, self.interval_unit)
        return self


class ItemUpdateRequest(BaseModel):
    id: str
    url: str
    interval_value: int
    interval_unit: Literal["seconds", "minutes", "hours"]

    @model_validator(mode="after")
    def check_min_interval(self) -> "ItemUpdateRequest":
        validate_interval(self.interval_value, self.interval_unit)
        return self


class ItemDeleteRequest(BaseModel):
    id: str
    size: str


class TrackedItem(BaseModel):
    url: str
    sizes: List[str]
    interval_seconds: int


class ItemListResponse(BaseModel):
    items: Dict[str, TrackedItem]


class ItemActionResponse(BaseModel):
    success: bool
    message: str
