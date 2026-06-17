from contextlib import asynccontextmanager
from pathlib import Path
import time

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import create_db_and_tables
from app.routes.ai import router as ai_router
from app.routes.dashboard import router as dashboard_router
from app.routes.fixtures import router as fixtures_router
from app.routes.insights import router as insights_router
from app.routes.metrics import router as metrics_router
from app.routes.notifications import router as notifications_router
from app.routes.players import router as players_router
from app.routes.standings import router as standings_router
from app.services.metrics_service import record_http_request_metrics


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


@app.middleware("http")
async def collect_request_metrics(request: Request, call_next):
    start_time = time.perf_counter()
    response = None

    try:
        response = await call_next(request)
        return response

    finally:
        duration_seconds = time.perf_counter() - start_time
        status_code = response.status_code if response is not None else 500

        record_http_request_metrics(
            request=request,
            status_code=status_code,
            duration_seconds=duration_seconds,
        )


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root():
    return {
        "message": "World Cup 2026 AI Stats API",
        "status": "running",
        "version": settings.app_version,
        "dashboard": "/dashboard",
        "fixtures": "/fixtures",
        "standings": "/standings",
        "group_insights": "/insights/groups",
        "player_stats": "/players/stats",
        "metrics": "/metrics",
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
app.include_router(insights_router)
app.include_router(metrics_router)
app.include_router(notifications_router)
app.include_router(players_router)
app.include_router(standings_router)
