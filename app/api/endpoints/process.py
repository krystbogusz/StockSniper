from fastapi import APIRouter, HTTPException
from app.schemas.process import ProcessStatusResponse, ProcessActionResponse
from app.core.process_manager import process_manager
from app.core.logger import api_logger

router = APIRouter()


@router.post("/start", response_model=ProcessActionResponse)
async def start_process():
    api_logger.info("Received request to start background process")
    success, message = process_manager.start()
    if not success:
        api_logger.warning(f"Failed to start process: {message}")
        raise HTTPException(status_code=400, detail=message)
    api_logger.info("Background process started successfully")
    return ProcessActionResponse(success=success, message=message)


@router.post("/stop", response_model=ProcessActionResponse)
async def stop_process():
    api_logger.info("Received request to stop background process")
    success, message = process_manager.stop()
    if not success:
        api_logger.warning(f"Failed to stop process: {message}")
        raise HTTPException(status_code=400, detail=message)
    api_logger.info("Background process stopped successfully")
    return ProcessActionResponse(success=success, message=message)


@router.post("/restart", response_model=ProcessActionResponse)
async def restart_process():
    api_logger.info("Received request to restart background process")
    success, message = process_manager.restart()
    if not success:
        api_logger.warning(f"Failed to restart process: {message}")
        raise HTTPException(status_code=400, detail=message)
    api_logger.info("Background process restarted successfully")
    return ProcessActionResponse(success=success, message=message)


@router.get("/status", response_model=ProcessStatusResponse)
async def get_status():
    api_logger.info("Received request for process status")
    is_running = process_manager.is_running()
    pid = process_manager.get_pid()
    message = "Process is running." if is_running else "Process is not running."

    return ProcessStatusResponse(is_running=is_running, pid=pid, message=message)


import time
from app.core.email_client import send_email

last_health_email_time = 0


@router.get("/health")
async def health_check():
    global last_health_email_time
    is_running = process_manager.is_running()

    if not is_running:
        current_time = time.time()
        if current_time - last_health_email_time > 3600:
            send_email(
                "StockSniper ALERT: Monitor is DOWN",
                "The background monitoring script has stopped running or crashed. Please log in and restart it.",
            )
            last_health_email_time = current_time
        return {"status": "down", "message": "Monitor script is not running."}

    return {"status": "ok", "message": "Monitor script is running smoothly."}
