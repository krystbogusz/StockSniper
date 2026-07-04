from fastapi import APIRouter, HTTPException
from app.schemas.item import ItemRequest, ItemActionResponse, ItemListResponse
from app.core.item_manager import item_manager

router = APIRouter()

@router.post("/add", response_model=ItemActionResponse)
async def add_item(request: ItemRequest):
    success, message = item_manager.add_item(request.url)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return ItemActionResponse(success=success, message=message)

@router.post("/delete", response_model=ItemActionResponse)
async def delete_item(request: ItemRequest):
    success, message = item_manager.delete_item(request.url)
    if not success:
        raise HTTPException(status_code=404, detail=message)
    return ItemActionResponse(success=success, message=message)

@router.get("/list", response_model=ItemListResponse)
async def list_items():
    items = item_manager.list_items()
    return ItemListResponse(items=items)
