import asyncio
from fastapi import APIRouter, HTTPException
from app.schemas.item import ItemRequest, ItemUpdateRequest, ItemActionResponse, ItemListResponse
from app.core.item_manager import item_manager
from app.core.llm_client import check_url_safety
from app.core.logger import api_logger

router = APIRouter()

def get_seconds(value: int, unit: str) -> int:
    multiplier = {"seconds": 1, "minutes": 60, "hours": 3600}[unit]
    return value * multiplier

@router.post("/add", response_model=ItemActionResponse)
async def add_item(request: ItemRequest):
    api_logger.info(f"Received request to add item: {request.url}")
    is_safe, reason = await asyncio.to_thread(check_url_safety, request.url)
    if not is_safe:
        api_logger.warning(f"URL rejected by security check: {request.url} - {reason}")
        raise HTTPException(status_code=400, detail=f"URL rejected by security check: {reason}")
        
    interval_sec = get_seconds(request.interval_value, request.interval_unit)
    success, message = item_manager.add_item(request.url, request.size, interval_sec)
    if not success:
        api_logger.error(f"Failed to add item {request.url}: {message}")
        raise HTTPException(status_code=400, detail=message)
        
    api_logger.info(f"Item added successfully: {request.url}")
    return ItemActionResponse(success=success, message=message)

@router.post("/update", response_model=ItemActionResponse)
async def update_item(request: ItemUpdateRequest):
    api_logger.info(f"Received request to update item ID: {request.id}")
    is_safe, reason = await asyncio.to_thread(check_url_safety, request.url)
    if not is_safe:
        api_logger.warning(f"URL rejected by security check for ID {request.id}: {reason}")
        raise HTTPException(status_code=400, detail=f"URL rejected by security check: {reason}")
        
    interval_sec = get_seconds(request.interval_value, request.interval_unit)
    success, message = item_manager.update_item(request.id, request.url, interval_sec)
    if not success:
        api_logger.error(f"Failed to update item {request.id}: {message}")
        raise HTTPException(status_code=400, detail=message)
        
    api_logger.info(f"Item {request.id} updated successfully")
    return ItemActionResponse(success=success, message=message)

@router.post("/delete", response_model=ItemActionResponse)
async def delete_item(request: ItemRequest):
    api_logger.info(f"Received request to delete item: {request.url}")
    success, message = item_manager.delete_item(request.url, request.size)
    if not success:
        api_logger.warning(f"Failed to delete item {request.url}: {message}")
        raise HTTPException(status_code=404, detail=message)
        
    api_logger.info(f"Item deleted successfully: {request.url}")
    return ItemActionResponse(success=success, message=message)

@router.get("/list", response_model=ItemListResponse)
async def list_items():
    api_logger.info("Received request to list items")
    items = item_manager.list_items()
    return ItemListResponse(items=items)
