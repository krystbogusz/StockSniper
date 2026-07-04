from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from app.api.endpoints import process, item
from app.api.dependencies import verify_basic, verify_bearer
from app.core.config import settings

app = FastAPI(
    title=settings.project_name,
    description="API for managing machine processes and watchlists.",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.include_router(
    process.router, 
    prefix="/process", 
    tags=["Process Management"],
    dependencies=[Depends(verify_bearer)]
)

app.include_router(
    item.router, 
    prefix="/item", 
    tags=["Item Watchlist"],
    dependencies=[Depends(verify_bearer)]
)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(verify_basic)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(username: str = Depends(verify_basic)):
    return JSONResponse(get_openapi(title="StockSniper API", version="1.0.0", routes=app.routes))
