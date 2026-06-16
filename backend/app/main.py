from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import create_db_and_tables
from app.routes.ai import router as ai_router
from app.routes.dashboard import router as dashboard_router
from app.routes.fixtures import router as fixtures_router
from app.routes.notifications import router as notifications_router


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.app_env != "test":
        create_db_and_tables()

    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root():
    return {
        "message": "World Cup 2026 AI Stats API",
        "status": "running",
        "version": settings.app_version,
        "dashboard": "/dashboard",
        "ai_summary": "/ai/fixtures/summary",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "backend",
        "version": settings.app_version,
    }


app.include_router(ai_router)
app.include_router(dashboard_router)
app.include_router(fixtures_router)
app.include_router(notifications_router)