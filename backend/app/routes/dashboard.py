from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def dashboard():
    dashboard_path = Path(__file__).resolve().parent.parent / "static" / "dashboard.html"
    return FileResponse(dashboard_path)