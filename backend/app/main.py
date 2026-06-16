from fastapi import FastAPI

from app.config import settings
from app.routes.fixtures import router as fixtures_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
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