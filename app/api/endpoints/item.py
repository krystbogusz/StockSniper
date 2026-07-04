import asyncio
from fastapi import APIRouter, HTTPException
from app.schemas.item import ItemRequest, ItemUpdateRequest, ItemActionResponse, ItemListResponse
from app.core.item_manager import item_manager
from app.core.llm_client import check_url_safety

router = APIRouter()

def get_seconds(value: int, unit: str) -> int:
    multiplier = {"seconds": 1, "minutes": 60, "hours": 3600}[unit]
    return value * multiplier

@router.post("/add", response_model=ItemActionResponse)
async def add_item(request: ItemRequest):
    is_safe, reason = await asyncio.to_thread(check_url_safety, request.url)
    if not is_safe:
        raise HTTPException(status_code=400, detail=f"URL rejected by security check: {reason}")
        
    interval_sec = get_seconds(request.interval_value, request.interval_unit)
    success, message = item_manager.add_item(request.url, request.size, interval_sec)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return ItemActionResponse(success=success, message=message)

@router.post("/update", response_model=ItemActionResponse)
async def update_item(request: ItemUpdateRequest):
    is_safe, reason = await asyncio.to_thread(check_url_safety, request.url)
    if not is_safe:
        raise HTTPException(status_code=400, detail=f"URL rejected by security check: {reason}")
        
    interval_sec = get_seconds(request.interval_value, request.interval_unit)
    success, message = item_manager.update_item(request.id, request.url, interval_sec)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return ItemActionResponse(success=success, message=message)

@router.post("/delete", response_model=ItemActionResponse)
async def delete_item(request: ItemRequest):
    success, message = item_manager.delete_item(request.url, request.size)
    if not success:
        raise HTTPException(status_code=404, detail=message)
    return ItemActionResponse(success=success, message=message)

@router.get("/list", response_model=ItemListResponse)
async def list_items():
    items = item_manager.list_items()
    return ItemListResponse(items=items)
