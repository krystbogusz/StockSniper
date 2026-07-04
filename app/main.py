from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from app.api.endpoints import process, item, settings as app_settings
from app.api.dependencies import verify_basic, verify_bearer
from app.core.config import settings
from app.core.logger import api_logger

from contextlib import asynccontextmanager
import asyncio
from datetime import datetime, timedelta


async def _health_check_loop():
    from app.api.endpoints.process import health_check

    while True:
        now = datetime.now()
        t1 = now.replace(hour=8, minute=0, second=0, microsecond=0)
        t2 = now.replace(hour=20, minute=0, second=0, microsecond=0)

        if now < t1:
            next_run = t1
        elif now < t2:
            next_run = t2
        else:
            next_run = t1 + timedelta(days=1)

        sleep_seconds = (next_run - now).total_seconds()
        api_logger.info(
            f"Next automatic health check scheduled at {next_run.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await asyncio.sleep(sleep_seconds)

        api_logger.info("Executing scheduled health check...")
        try:
            await health_check()
        except Exception as e:
            api_logger.error(f"Error in scheduled health check: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    api_logger.info("FastAPI Application startup")
    task = asyncio.create_task(_health_check_loop())
    yield
    task.cancel()


app = FastAPI(
    title=settings.project_name,
    description="API for managing machine processes and watchlists.",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)

app.include_router(
    process.router,
    prefix="/process",
    tags=["Process Management"],
    dependencies=[Depends(verify_bearer)],
)

app.include_router(
    item.router,
    prefix="/item",
    tags=["Item Watchlist"],
    dependencies=[Depends(verify_bearer)],
)

app.include_router(
    app_settings.router,
    prefix="/settings",
    tags=["Settings"],
    dependencies=[Depends(verify_bearer)],
)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(verify_basic)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(username: str = Depends(verify_basic)):
    return JSONResponse(
        get_openapi(title="StockSniper API", version="1.0.0", routes=app.routes)
    )
