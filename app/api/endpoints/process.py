from fastapi import APIRouter, HTTPException
from app.schemas.process import ProcessStatusResponse, ProcessActionResponse
from app.core.process_manager import process_manager

router = APIRouter()

@router.post("/start", response_model=ProcessActionResponse)
async def start_process():
    success, message = process_manager.start()
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return ProcessActionResponse(success=success, message=message)

@router.post("/stop", response_model=ProcessActionResponse)
async def stop_process():
    success, message = process_manager.stop()
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return ProcessActionResponse(success=success, message=message)

@router.get("/status", response_model=ProcessStatusResponse)
async def get_status():
    is_running = process_manager.is_running()
    pid = process_manager.get_pid()
    message = "Process is running." if is_running else "Process is not running."
    
    return ProcessStatusResponse(
        is_running=is_running,
        pid=pid,
        message=message
    )
