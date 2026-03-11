from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.settings import get_settings

router = APIRouter(tags=["Base"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/")
def root() -> dict[str, str]:
    settings = get_settings()
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "docs": f"{settings.app_root_path}/docs",
    }