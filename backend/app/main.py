from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import create_db_and_tables
from app.routes.fixtures import router as fixtures_router


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


@app.get("/")
def root():
    return {
        "message": "World Cup 2026 AI Stats API",
        "status": "running",
        "version": settings.app_version,
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "backend",
        "version": settings.app_version,
    }


app.include_router(fixtures_router)