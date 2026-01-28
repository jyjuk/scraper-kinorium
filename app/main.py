"""
Main FastAPI application module.
"""
import sys
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.models.database import init_db
from app.routers import scraper
from app.models.schemas import HealthResponse

# Fix for Windows event loop policy (required for Playwright subprocess)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Initializes database on startup.
    """
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Async REST API service for scraping ua.kinorium.com",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scraper.router, prefix="/api/v1", tags=["scraper"])


@app.get("/", response_model=HealthResponse)
async def root():
    """
    Root endpoint - health check.

    Returns:
        HealthResponse: Service status information
    """
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint.

    Returns:
        HealthResponse: Service status information
    """
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version="1.0.0"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
